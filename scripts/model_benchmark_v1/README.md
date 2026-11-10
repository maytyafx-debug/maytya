# METATYA MODEL BENCHMARK V1

An isolated, manual, review-only benchmark. It does not modify Content Engine V1/V2,
the website, publication files, or Telegram.

## Candidate models

The initial candidate list is in `models.json`. It is intentionally small and
uses one OpenRouter key so that each model receives the same three tasks.

The initial set includes:
- NVIDIA Nemotron 3 Ultra (free)
- NVIDIA Nemotron 3.5 Super VL (free)
- Google Gemma 4 26B A4B (free)
- Xing4.0 29B A4B (free; current baseline)

Model availability and free-tier limits change. Confirm the live model catalog
before a benchmark run.

## Run locally

From the repository root:

```bash
python -m pip install requests
export OPENROUTER_API_KEY="..."
python scripts/model_benchmark_v1/run.py
```

The default run makes 12 calls (4 models × 3 tasks). Each candidate receives
the exact same prompt for each task. HTTP 429 is recorded and does not stop
the remaining comparisons. The script does not retry 429, to avoid burning
additional free-tier quota.

Output: `out/model-benchmark-v1.json`.

## Manual GitHub Actions run

Use **METATYA Model Benchmark V1 — Manual**. It requires the existing
`OPENROUTER_API_KEY` repository secret and uploads a seven-day artifact.
It does not commit output, publish content, send Telegram messages, or write
to `docs/content.json`.

## Scoring limits

The deterministic score checks JSON structure, Persian-language signal,
length, three short-script lines, allowed source IDs, and selected safety
phrases. It is not a factual-accuracy score. Source URLs are metadata only;
the benchmark does not check whether a source supports a claim. Human review
and a separate claim-verification system remain mandatory.

## Privacy and security

Never put API keys in files, prompts, artifacts, or logs. The workflow passes
the key only through the Actions secret environment. Generated outputs are
stored as a private workflow artifact only if repository visibility and
Actions settings permit; review repository access before running sensitive
tests.
