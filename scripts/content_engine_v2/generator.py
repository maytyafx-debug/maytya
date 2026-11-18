"""Generate, diagnose, revise, and re-check a single review-only V2 item."""
from __future__ import annotations
from .profiles import build_prompt
from .providers import generate_json, resolve_sources
from .schema import make_item
from .quality import evaluate, required_disclaimer
from .source_registry import verify_source


def generate_item(*, domain: str, tab: str, audience: str, source_pack: list[dict],
                  history_titles: list[str] | None = None, existing_items: list[dict] | None = None,
                  formats: list[str] | None = None, provider=None, max_revisions: int = 2) -> dict:
    """Bounded self-correction: regenerate the whole draft using explicit gate errors.

    The system never patches factual prose itself. It asks the model to revise, then
    reruns source verification and every deterministic quality check. Exhaustion fails closed.
    """
    if max_revisions < 0 or max_revisions > 3:
        raise ValueError("max_revisions باید بین صفر تا سه باشد")
    base_prompt = build_prompt(domain=domain, tab=tab, audience=audience,
                               source_pack=source_pack, history_titles=history_titles)
    call_provider = provider or generate_json
    repair_history = []
    feedback = ""
    last_item = None
    for attempt in range(max_revisions + 1):
        prompt = base_prompt
        if feedback:
            prompt += (
                "\n\nبازبینی خودکار نسخه قبلی: موارد زیر در کنترل کیفیت رد شدند. "
                "کل محتوا را از نو و با اصلاح دقیق تولید کن؛ عدد یا منبع را حدس نزن. "
                "اگر اطلاعات کافی برای اصلاح نداری، ادعا را حذف کن یا محدودیت را شفاف بنویس. "
                "فقط از شناسه‌های منبع مجاز استفاده کن.\n"
                + feedback
            )
        response = call_provider(prompt)
        try:
            sources = resolve_sources(response.get("source_ids", []), source_pack)
            verified_sources = []
            for source in sources:
                verification = verify_source(source)
                if not verification.get("ok"):
                    raise RuntimeError("منبع انتخابی قابل تأیید نیست: " + str(verification.get("reason")))
                verified_sources.append({**source, "verified": True, "verified_status": verification.get("status"),
                                         "content_type": verification.get("content_type"),
                                         "checked_title": verification.get("title")})
            disclaimer = required_disclaimer(domain)
            item = make_item(domain=domain, tab=tab, title=response.get("title",""),
                body=response.get("body",""), audience=audience, formats=formats or ["website","telegram"],
                short_script=response.get("short_script",[]), sources=verified_sources, disclaimer=disclaimer,
                status="draft")
            item["provider"] = response.get("_provider", "custom")
            item["model"] = response.get("_model", "unspecified")
            report = evaluate(item, existing_titles=set(history_titles or []),
                              existing_items=existing_items or [])
            item["quality"] = report
            last_item = item
            if report["ok"]:
                item["status"] = "review"
                item["repair"] = {"attempts": attempt, "history": repair_history,
                                  "outcome": "passed_after_revision" if attempt else "passed_first_try"}
                return item
            feedback = "\n".join("- " + error for error in report["errors"])
        except Exception as exc:
            feedback = "خطای اعتبارسنجی منبع/ساختار: " + str(exc)[:400]
            last_item = None
        repair_history.append({"attempt": attempt + 1, "feedback": feedback[:1000]})
    if last_item is None:
        raise RuntimeError("اصلاح خودکار پس از تلاش‌های محدود موفق نشد؛ مورد برای بازبینی انسانی تولید نشد. "
                           + (feedback[:500] if feedback else "خطای اعتبارسنجی"))
    last_item["status"] = "draft"
    last_item["repair"] = {"attempts": max_revisions, "history": repair_history,
                           "outcome": "blocked_after_revisions"}
    return last_item
