"""Offline tests for OpenRouter model fallback; no API calls or secrets required."""
import os
import unittest
from unittest.mock import patch

import requests

from scripts.content_engine_v2.providers import (
    DEFAULT_MODELS,
    FREE_FALLBACK_ROUTER,
    configured_models,
    generate_json,
)


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {
            "choices": [{"message": {"content": '{"title":"آزمایش"}'}}]
        }

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(kwargs["json"]["model"])
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class OpenRouterFallbackTests(unittest.TestCase):
    def test_empty_model_setting_uses_benchmarked_candidate_and_free_router(self):
        with patch.dict(os.environ, {"OPENROUTER_MODELS": ""}):
            self.assertEqual(
                configured_models(),
                DEFAULT_MODELS + [FREE_FALLBACK_ROUTER],
            )

    def test_explicit_models_are_deduplicated_and_router_is_appended(self):
        with patch.dict(
            os.environ,
            {"OPENROUTER_MODELS": "provider/one, provider/two,provider/one"},
        ):
            self.assertEqual(
                configured_models(),
                ["provider/one", "provider/two", FREE_FALLBACK_ROUTER],
            )

    def test_rate_limit_moves_to_next_model_without_retrying_same_model(self):
        session = FakeSession([
            FakeResponse(429),
            FakeResponse(200),
        ])
        result = generate_json("prompt", api_key="test-key",
                               models=["provider/limited", FREE_FALLBACK_ROUTER],
                               session=session)
        self.assertEqual(session.calls, ["provider/limited", FREE_FALLBACK_ROUTER])
        self.assertEqual(result["_model"], FREE_FALLBACK_ROUTER)

    def test_missing_model_moves_to_next_candidate(self):
        session = FakeSession([
            FakeResponse(404),
            FakeResponse(200),
        ])
        result = generate_json("prompt", api_key="test-key",
                               models=["provider/retired", FREE_FALLBACK_ROUTER],
                               session=session)
        self.assertEqual(session.calls, ["provider/retired", FREE_FALLBACK_ROUTER])
        self.assertEqual(result["_model"], FREE_FALLBACK_ROUTER)

    def test_provider_error_moves_to_next_candidate(self):
        session = FakeSession([
            FakeResponse(503),
            FakeResponse(200),
        ])
        result = generate_json("prompt", api_key="test-key",
                               models=["provider/unavailable", FREE_FALLBACK_ROUTER],
                               retries_per_model=1, session=session)
        self.assertEqual(session.calls, ["provider/unavailable", FREE_FALLBACK_ROUTER])
        self.assertEqual(result["_model"], FREE_FALLBACK_ROUTER)

    def test_all_models_failing_raises_instead_of_fabricating_success(self):
        session = FakeSession([FakeResponse(429), FakeResponse(503)])
        with self.assertRaises(RuntimeError):
            generate_json("prompt", api_key="test-key",
                          models=["provider/limited", FREE_FALLBACK_ROUTER],
                          retries_per_model=1, session=session)

    def test_missing_key_makes_no_request(self):
        session = FakeSession([])
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                generate_json("prompt", session=session)
        self.assertEqual(session.calls, [])


if __name__ == "__main__":
    unittest.main()
