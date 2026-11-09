"""Channel renderers; keep one approved source item and derive platform-specific copy."""
from __future__ import annotations
import html


def render_telegram(item: dict, site_url: str = "") -> str:
    title = html.escape(item["title"])
    body = html.escape(item["body"])
    link = html.escape(site_url, quote=True)
    disclaimer = html.escape(item.get("disclaimer") or "")
    parts = [f"📌 <b>{title}</b>", "", body]
    if link: parts += ["", f'👉 <a href="{link}">مطالعه نسخه کامل</a>']
    if disclaimer: parts += ["", f"<i>{disclaimer}</i>"]
    return "\n".join(parts)


def render_reel(item: dict) -> dict:
    script = item.get("short_script") or []
    return {"hook": script[0] if len(script)>0 else "",
            "lesson": script[1] if len(script)>1 else "",
            "closing": script[2] if len(script)>2 else "",
            "caption": item["title"] + "\n\n" + item["body"],
            "disclaimer": item.get("disclaimer", "")}


def render_carousel(item: dict) -> list[dict]:
    body = item["body"].strip()
    # Never invent extra claims: use the supplied title and body as one source of truth.
    chunks = [body[i:i+220].strip() for i in range(0, len(body), 220)]
    slides = [{"type":"cover", "text":item["title"]}]
    slides.extend({"type":"content", "text":chunk} for chunk in chunks)
    slides.append({"type":"closing", "text":"برای یادگیری عمیق‌تر، منبع و محدودیت‌های موضوع را بررسی کن."})
    return slides


def render_all(item: dict, site_url: str = "") -> dict:
    output = {}
    for channel in item.get("formats", []):
        if channel == "telegram": output[channel] = render_telegram(item, site_url)
        elif channel == "instagram_reel" or channel == "youtube_short": output[channel] = render_reel(item)
        elif channel == "instagram_carousel": output[channel] = render_carousel(item)
        elif channel == "website": output[channel] = {"title":item["title"], "body":item["body"], "sources":item.get("sources", [])}
    return output
