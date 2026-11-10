"""Canonical V2 content schema and backward-compatible V1 adapter."""
from __future__ import annotations
import hashlib, json, re, unicodedata
from datetime import datetime, timezone

SCHEMA_VERSION = "metatya.content.v2"
AUDIENCES = {"beginner", "intermediate", "professional", "sport_beginner", "sport_advanced", "sport_national", "sport_olympic"}
CHANNELS = {"website", "telegram", "instagram_reel", "instagram_carousel", "youtube_short"}
STATUSES = {"draft", "review", "approved", "published", "rejected"}


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", str(value or "")).replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"[\s‌ـ\u200f\u200e]+", "", value).casefold()


def stable_id(domain: str, tab: str, title: str) -> str:
    raw = "|".join((domain, tab, normalize_text(title))).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def make_item(*, domain: str, tab: str, title: str, body: str, audience: str = "beginner",
              formats: list[str] | None = None, short_script: list[str] | None = None,
              sources: list[dict] | None = None, tags: list[str] | None = None,
              disclaimer: str = "", status: str = "draft", created_at: str | None = None) -> dict:
    now = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {
        "id": stable_id(domain, tab, title), "schema": SCHEMA_VERSION,
        "domain": domain, "tab": tab, "audience": audience,
        "title": title.strip(), "body": body.strip(),
        "formats": formats or ["website", "telegram"],
        "short_script": short_script or [], "sources": sources or [],
        "tags": tags or [], "disclaimer": disclaimer,
        "status": status, "created_at": now, "updated_at": now,
        "quality": {"score": None, "checks": {}, "reviewer": None},
    }


def to_v1(item: dict, *, date: str | None = None) -> dict:
    """Render an approved V2 item into the existing docs/content.json item shape."""
    stamp = item.get("created_at", "")
    day = date or (stamp[:10] if stamp else datetime.now(timezone.utc).date().isoformat())
    body = item["body"]
    disclaimer = item.get("disclaimer") or ""
    if disclaimer and disclaimer not in body:
        body = body.rstrip() + "\n\n" + disclaimer
    return {
        "title": item["title"], "body": body, "tab": item["tab"],
        "provider": "metatya-content-engine-v2", "date": day,
        "short_script": list(item.get("short_script") or []),
        "tg": item.get("channel_copy", {}).get("telegram", ""),
        "v2_id": item.get("id"), "audience": item.get("audience", "beginner"),
    }


def dump_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
