# METATYA RMO + Knowledge Bridge V1

A standalone, provider-agnostic foundation for bounded model fallback and
explicitly curated project knowledge. This V1 is an orchestration core, not a
production API integration.

## Guarantees

- At most `max_attempts` enabled candidates are called, each no more than once.
- Retryable provider failures, timeouts, connection errors, and invalid outputs
  move to the next candidate.
- Non-retryable provider failures stop immediately to avoid wasting quota.
- The loop is finite and fails closed when no candidate produces valid output.
- Provider exception text is not copied into result logs.
- Knowledge is passed only when records are explicitly marked
  `review_status: approved`; incomplete and duplicate records are ignored.
- The bridge does not access ChatGPT private chat history, personal memory,
  connected accounts, or secrets. Knowledge must be deliberately exported or
  authored into a METATYA-controlled store.

## Provider adapter contract

Inject a callable with signature
`provider_call(model_id, request, approved_knowledge)`. It should raise
`ProviderFailure(code, message, retryable, http_status)` for known provider
failures, or return the raw model result. Supply a separate validator that
returns true only when the response meets the task's structural requirements.
The core performs no network requests and stores no API keys.

## Deliberate V1 limitations

- No OpenRouter or OpenAI network adapter is enabled.
- No automatic retries against the same model.
- No persistent circuit-breaker state or model ranking yet.
- Structural validation is not factual verification. A separate source/claim
  verification stage and human review are required.
- No automatic publication, Telegram posting, or Content Engine integration.

## Tests

```bash
python -m unittest discover -s scripts/metatya_rmo_v1 -p 'test_*.py' -v
```
