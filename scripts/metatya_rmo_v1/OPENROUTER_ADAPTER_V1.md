# METATYA OpenRouter Adapter V1

This adapter is an optional transport layer for the already-merged RMO core.
It is deliberately disabled unless the host explicitly constructs and calls it.

## Contract

`OpenRouterChatAdapter` implements the RMO provider callable:
`adapter(model_id, request, approved_knowledge)`.

- Uses the OpenRouter OpenAI-compatible chat-completions endpoint.
- Reads `OPENROUTER_API_KEY` from the process environment at call time, unless
  an explicit key is injected by the host for testing.
- Does not make requests at import time and does not store credentials.
- Uses a finite HTTP timeout and caps response bytes.
- Does not log prompts, response bodies, or credentials.
- 401/403 are non-retryable authentication failures; 404 is model-specific and advances to the next RMO candidate (the same model is never retried).
- 429, selected transient statuses, and 5xx are retryable by the outer RMO;
  this adapter itself never retries.
- Network/timeout failures are normalized for the RMO.
- Only approved knowledge supplied by the Knowledge Bridge is included, as
  reference material rather than instructions.

## Model ID note

The OpenRouter model page currently documents the free slug
`xingchen-agi/xing4.0-29b-a4b:free`. Model availability and free-tier limits
can change. Do not infer availability from a successful catalog lookup; use
controlled preflight checks before enabling any model in a runtime allowlist.

## Safety and rollout

- No live API request is part of unit tests or CI.
- No secret is added to GitHub files or requested in chat.
- Do not connect this adapter to the website, Content Engine, Telegram, or
  production workflows in this phase.
- The caller must still provide a structural validator; factual/source
  verification and human review remain separate mandatory gates.
- The adapter does not grant access to ChatGPT chat history or personal memory.

## Tests

```bash
python -m unittest discover -s scripts/metatya_rmo_v1 -p 'test_*.py' -v
```
