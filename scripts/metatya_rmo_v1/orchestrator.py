"""Provider-agnostic, bounded model fallback orchestration.

This module deliberately does not make network calls. Provider adapters are
injected by the host application, keeping credentials and provider policy out
of the orchestration core.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class ModelCandidate:
    model_id: str
    provider: str
    enabled: bool = True


@dataclass
class ProviderFailure(Exception):
    code: str
    message: str = ""
    retryable: bool = True
    http_status: int | None = None

    def __str__(self) -> str:
        return self.message or self.code


@dataclass
class Attempt:
    model_id: str
    provider: str
    status: str
    error_code: str | None = None
    http_status: int | None = None


@dataclass
class OrchestrationResult:
    status: str
    output: Any = None
    selected_model: str | None = None
    attempts: list[Attempt] = field(default_factory=list)
    reason: str | None = None


Provider = Callable[[str, Any, list[dict[str, str]]], Any]
Validator = Callable[[Any], bool]


class ResilientModelOrchestrator:
    """Try each eligible model at most once, then fail closed."""

    def __init__(
        self,
        candidates: Iterable[ModelCandidate],
        provider_call: Provider,
        validator: Validator,
        *,
        max_attempts: int = 4,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.candidates = tuple(candidates)
        self.provider_call = provider_call
        self.validator = validator
        self.max_attempts = max_attempts

    def run(self, request: Any, *, knowledge: list[dict[str, str]] | None = None) -> OrchestrationResult:
        context = knowledge or []
        candidates = [item for item in self.candidates if item.enabled][: self.max_attempts]
        attempts: list[Attempt] = []

        if not candidates:
            return OrchestrationResult(status="failed", attempts=[], reason="no_eligible_models")

        for candidate in candidates:
            try:
                output = self.provider_call(candidate.model_id, request, context)
            except ProviderFailure as exc:
                attempts.append(Attempt(
                    model_id=candidate.model_id,
                    provider=candidate.provider,
                    status="provider_error",
                    error_code=exc.code,
                    http_status=exc.http_status,
                ))
                # Non-retryable errors are model/configuration-independent
                # (for example invalid credentials); do not waste other quotas.
                if not exc.retryable:
                    return OrchestrationResult(
                        status="failed", attempts=attempts, reason="non_retryable_provider_error"
                    )
                continue
            except TimeoutError:
                attempts.append(Attempt(candidate.model_id, candidate.provider, "timeout", "timeout"))
                continue
            except ConnectionError:
                attempts.append(Attempt(candidate.model_id, candidate.provider, "connection_error", "connection_error"))
                continue
            except Exception:
                # Do not leak provider exception text, prompts, or credentials.
                attempts.append(Attempt(candidate.model_id, candidate.provider, "provider_error", "unexpected_error"))
                continue

            try:
                valid = bool(self.validator(output))
            except Exception:
                valid = False
            if not valid:
                attempts.append(Attempt(candidate.model_id, candidate.provider, "invalid_output", "validation_failed"))
                continue

            attempts.append(Attempt(candidate.model_id, candidate.provider, "accepted"))
            return OrchestrationResult(
                status="accepted",
                output=output,
                selected_model=candidate.model_id,
                attempts=attempts,
            )

        return OrchestrationResult(
            status="failed",
            attempts=attempts,
            reason="all_candidates_exhausted",
        )
