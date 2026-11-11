# METATYA MODEL BENCHMARK V1

An isolated, manual, review-only benchmark. It does not modify Content Engine V1/V2,
website content, publication files, or Telegram.

## Candidates and tasks

The model list is in `models.json`; three fixed Persian tasks are in `prompts.json`.
The pilot compares four candidates across AI literacy, general financial literacy,
and age-aware sport/health literacy. The multimodal candidate receives text-only
prompts in V1 and is therefore not undergoing a vision benchmark.

## Run locally

```bash
python -m pip install requests
export OPENROUTER_API_KEY="..."
python scripts/model_benchmark_v1/run.py
```

The default run makes 12 calls. Each model receives the same prompt per task.
HTTP 429 is recorded and is not retried, avoiding unnecessary free-tier quota use.

## Manual GitHub Actions run

Use **METATYA Model Benchmark V1 — Manual**. It requires the repository secret
`OPENROUTER_API_KEY`. The workflow is manual-only, read-only with respect to
repository contents, and uploads a seven-day artifact. It does not commit output,
publish content, send Telegram messages, or write to production content files.

## Scoring and limitations

The reported `format_guardrail_score` checks required JSON keys, non-empty fields,
length, three script lines, Persian text signal, non-empty allowlisted source IDs,
and selected safety phrases. It is not a factual-accuracy score, source-support
verification, or editorial/publication approval. Source URLs are metadata only;
the benchmark does not fetch them or validate claims against their contents.
Human review and a separate claim-verification system remain mandatory.

Free model availability, pricing, and rate limits can change. Confirm live access
before running. Never put API keys in files, prompts, artifacts, or logs.
