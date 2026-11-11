"""Read-only bridge for explicitly approved, project-curated knowledge records."""
from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = {"id", "title", "content", "source", "review_status"}


def prepare_knowledge(records: list[dict[str, Any]], *, max_records: int = 20) -> list[dict[str, str]]:
    """Return only reviewed records in a minimal prompt-safe representation.

    This function never reads ChatGPT private history or connected accounts.
    Records must be explicitly exported/curated into the host application's
    own store and marked review_status='approved'.
    """
    if max_records < 0:
        raise ValueError("max_records cannot be negative")
    if max_records == 0:
        return []

    approved: list[dict[str, str]] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or not REQUIRED_FIELDS.issubset(record):
            continue
        record_id = str(record.get("id", "")).strip()
        if not record_id or record_id in seen:
            continue
        if record.get("review_status") != "approved":
            continue
        title = str(record.get("title", "")).strip()
        content = str(record.get("content", "")).strip()
        source = str(record.get("source", "")).strip()
        if not title or not content or not source:
            continue
        seen.add(record_id)
        approved.append({
            "id": record_id,
            "title": title[:200],
            "content": content[:6000],
            "source": source[:500],
        })
        if len(approved) >= max_records:
            break
    return approved
