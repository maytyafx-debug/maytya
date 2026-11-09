"""End-to-end single-item generation into review-only V2 records."""
from __future__ import annotations
from .profiles import build_prompt
from .providers import generate_json, resolve_sources
from .schema import make_item
from .quality import evaluate, DISCLAIMERS

def generate_item(*, domain: str, tab: str, audience: str, source_pack: list[dict],
                  history_titles: list[str] | None = None, formats: list[str] | None = None,
                  provider=None) -> dict:
    prompt = build_prompt(domain=domain, tab=tab, audience=audience,
                          source_pack=source_pack, history_titles=history_titles)
    response = (provider or generate_json)(prompt)
    sources = resolve_sources(response.get("source_ids", []), source_pack)
    disclaimer = (DISCLAIMERS["financial"] if domain in {"forex","crypto","bourse","income","business","finance"}
                  else DISCLAIMERS["medical"] if domain in {"sport","health"}
                  else DISCLAIMERS["law"] if domain == "law" else "")
    item = make_item(domain=domain, tab=tab, title=response.get("title",""),
        body=response.get("body",""), audience=audience, formats=formats or ["website","telegram"],
        short_script=response.get("short_script",[]), sources=sources, disclaimer=disclaimer,
        status="draft")
    item["provider"] = response.get("_provider", "custom")
    item["model"] = response.get("_model", "unspecified")
    report = evaluate(item, existing_titles=set(history_titles or []))
    item["quality"] = report
    item["status"] = "review" if report["ok"] else "draft"
    return item
