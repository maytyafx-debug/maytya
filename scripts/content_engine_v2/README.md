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
Schema, audience/domain profiles, provider fallback, review-only batch generation, deterministic quality gate, source-ID validation, channel renderers, V1 compatibility adapter, and automated tests are implemented. An allowlisted HTTPS source verifier, curated official-source registry, near-duplicate comparison, and review-only batch generation are implemented. Source reachability is not a fact-check: editors must still confirm that each source supports the specific claims. Editorial UI, semantic evaluation against the full historical archive, and controlled V1 promotion remain later stages. No production workflow points to V2 yet.


## Source verification and duplicate checks

Check the curated source list:

```bash
python -m scripts.content_engine_v2.verify_sources scripts/content_engine_v2/examples/source-registry.json --output out/source-verification.json
```

The verifier only requests HTTPS URLs on an explicit official-domain allowlist, rejects redirects and private destinations, limits response reads, and reports whether the source endpoint is reachable. A reachable page is **not** proof that it supports an article's claims.

The quality gate compares new drafts against earlier items supplied to it. It uses normalized text, token overlap, and sequence similarity to flag likely near-duplicates; editors should review flagged matches and borderline cases.


## Explicit approval and reversible promotion

The generator never publishes. A human editor must review each draft, correct it, and set its `status` to `approved` in the reviewed JSON. Then create an approval file containing only the exact approved IDs:

```json
{"approved_ids":["item-id-reviewed-by-editor"]}
```

Preview the promotion first (dry-run is the default):

```bash
python -m scripts.content_engine_v2.promote out/reviewed-v2.json --approval-file approvals.json
```

Only after checking the preview, add `--apply` to write. The script makes a timestamped backup before the atomic replacement, inserts new items without truncating or deleting existing history, rejects items not explicitly marked approved, and refuses duplicate promotion. No GitHub workflow calls this command.
