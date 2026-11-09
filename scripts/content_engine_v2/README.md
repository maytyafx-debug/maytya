# METATYA CONTENT ENGINE 2.0 — GOLDEN EDITION

This package is an isolated V2 foundation. It does **not** replace or write to the V1 live file `docs/content.json`.

## Principles
- One canonical educational item; platform copies are derived from it.
- Audience tracks are explicit. Sports tracks stay distinct: beginner, advanced, national-level, Olympic.
- Source metadata, editorial checks, safety disclaimer, deduplication, and human approval are first-class fields.
- Financial topics are educational only: no personalized advice, trading signals, entry/exit instructions, guaranteed outcomes, or certain forecasts.
- Human review remains required; a passing automated check is not publication approval.

## Canonical item
See `schema.py` and `make_item()`. Required editorial fields include domain, tab, audience, title, body, formats, three-part short script, source records, disclaimer, and status.

## Generate review drafts
Prepare a manifest with `jobs[]`. Every job needs `domain`, `tab`, `audience`, and a `source_pack[]` containing records with `id`, `title`, and `url`. Source records must be collected and checked by the caller; the model is not allowed to invent source URLs.

```bash
export OPENROUTER_API_KEY="..."
export OPENROUTER_MODELS="provider/model-one,provider/model-two"
python -m scripts.content_engine_v2.generate_cli manifest.json --output out/content-v2-generated.json
```

The generator uses bounded retries and model fallback for rate limits/server errors. It fails closed instead of substituting fabricated fallback content. Every generated item remains a draft or review candidate.

## Quality gate
Run from repository root:

```bash
python -m scripts.content_engine_v2.engine out/content-v2-generated.json --output out/content-v2-review.json
```

The command writes only a review artifact. It never changes `docs/content.json` or sends posts. Human editorial approval is still required before any publication.

## Current stage
Schema, audience/domain profiles, provider fallback, review-only batch generation, deterministic quality gate, source-ID validation, channel renderers, V1 compatibility adapter, and automated tests are implemented. Automated source discovery/verification, semantic similarity detection, editorial UI, and controlled V1 promotion remain later stages. No production workflow points to V2 yet.
