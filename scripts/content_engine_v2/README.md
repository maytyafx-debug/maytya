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

## Quality gate
Run from repository root:

```bash
python -m scripts.content_engine_v2.engine path/to/staged-v2.json --output out/content-v2-review.json
```

Input format: `{"items": [{...canonical V2 item...}]}`. The command writes only the review artifact. It never changes `docs/content.json` or sends posts.

## Current stage
Schema, deterministic editorial gate, and channel renderers are implemented. Generation/provider orchestration, source verification, similarity detection beyond normalized exact titles, editorial UI, and controlled V1 promotion remain later stages. No production workflow points to V2 yet.
