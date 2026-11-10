"""Editorial quality gate. Deterministic checks only; human review remains mandatory."""
from __future__ import annotations
import re
from .schema import normalize_text
from .similarity import find_near_duplicates

BANNED = ("سود تضمینی", "تضمین سود", "بدون ریسک", "قطعاً سود", "قطعا سود", "درآمد تضمینی")
FINANCIAL = {"forex", "crypto", "bourse", "income", "business", "finance"}
MEDICAL = {"sport", "health"}
DISCLAIMERS = {
    "financial": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "medical": "این محتوا عمومی است و جایگزین نظر متخصص سلامت نیست.",
    "law": "این مطلب اطلاعات عمومی است و جایگزین مشاوره حقوقی نیست.",
}


def _sentences(script):
    return isinstance(script, list) and len(script) == 3 and all(isinstance(x, str) and 3 <= len(x.strip()) <= 160 for x in script)


def evaluate(item: dict, *, existing_titles: set[str] | None = None, existing_items: list[dict] | None = None, allowed_tabs: set[str] | None = None) -> dict:
    errors, checks = [], {}
    title, body = str(item.get("title", "")).strip(), str(item.get("body", "")).strip()
    domain, tab = item.get("domain"), item.get("tab")
    checks["title"] = bool(title and len(title) <= 110)
    if not checks["title"]: errors.append("عنوان خالی یا بیش از ۱۱۰ نویسه است.")
    checks["body_length"] = 100 <= len(body) <= 1800
    if not checks["body_length"]: errors.append("متن باید بین ۱۰۰ تا ۱۸۰۰ نویسه باشد.")
    checks["domain_tab"] = bool(domain and tab and (allowed_tabs is None or tab in allowed_tabs))
    if not checks["domain_tab"]: errors.append("حوزه یا تب نامعتبر است.")
    audience = item.get("audience")
    known_domains = {"forex","crypto","bourse","income","business","finance","education","psychology","law","ai","privacy","sport","health"}
    sport_audiences = {"sport_beginner","sport_advanced","sport_national","sport_olympic"}
    general_audiences = {"beginner","intermediate","professional"}
    checks["domain_known"] = domain in known_domains
    if not checks["domain_known"]: errors.append("حوزه محتوایی در فهرست رسمی Metatya نیست.")
    checks["audience"] = (audience in sport_audiences if domain == "sport" else audience in general_audiences)
    if not checks["audience"]: errors.append("سطح مخاطب معتبر نیست؛ مسیرهای ورزشی باید مستقل از مسیرهای عمومی انتخاب شوند.")
    checks["short_script"] = _sentences(item.get("short_script"))
    if not checks["short_script"]: errors.append("سناریوی کوتاه باید دقیقاً سه جمله معتبر داشته باشد.")
    combined = normalize_text(title + " " + body)
    banned = [p for p in BANNED if normalize_text(p) in combined]
    checks["claims"] = not banned
    if banned: errors.append("عبارت تبلیغاتی/وعده ممنوع: " + "، ".join(banned))
    required = DISCLAIMERS["financial"] if domain in FINANCIAL else DISCLAIMERS["medical"] if domain in MEDICAL else DISCLAIMERS["law"] if domain == "law" else ""
    disclaimer_text = str(item.get("disclaimer") or "")
    checks["disclaimer"] = not required or required in (body + " " + disclaimer_text)
    if not checks["disclaimer"]: errors.append("هشدار حوزه تخصصی درج نشده است.")
    sources = item.get("sources")
    checks["sources"] = isinstance(sources, list) and all(isinstance(s, dict) and s.get("title") and s.get("url") for s in sources)
    if not checks["sources"]: errors.append("منابع باید فهرست ساختاریافته عنوان و نشانی باشند؛ برای محتوای ماندگار منبع رسمی/معتبر ثبت شود.")
    known = existing_titles or set()
    normalized = normalize_text(title)
    checks["duplicate"] = bool(normalized) and normalized not in {normalize_text(x) for x in known}
    if not checks["duplicate"]: errors.append("عنوان خالی یا تکراری است.")
    near = find_near_duplicates(item, existing_items or [], threshold=0.65)
    checks["near_duplicate"] = not near
    if near: errors.append("محتوای بسیار مشابه با سابقه پیدا شد: " + "، ".join(x["title"] for x in near[:3]))
    formats = item.get("formats")
    checks["formats"] = isinstance(formats, list) and bool(formats) and set(formats) <= {"website","telegram","instagram_reel","instagram_carousel","youtube_short"}
    if not checks["formats"]: errors.append("قالب انتشار نامعتبر است.")
    score = round(100 * sum(bool(v) for v in checks.values()) / max(1, len(checks)))
    return {"ok": not errors, "score": score, "checks": checks, "errors": errors, "near_duplicates": near,
            "decision": "needs_human_review" if not errors else "eligible_for_human_review"}
