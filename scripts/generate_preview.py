
"""Safe Metatya preview. Never writes docs/content.json."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
LIVE_FILE = ROOT / "docs" / "content.json"
PREVIEW_FILE = ROOT / "out" / "preview-content.json"

sys.path.insert(0, str(SCRIPTS))
import generate as gen


def read_json(path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def selected_sections():
    raw = os.getenv("PREVIEW_SECTIONS", "forex,crypto")
    keys = list(dict.fromkeys(
        item.strip() for item in raw.split(",") if item.strip()
    ))

    if not keys:
        raise ValueError("هیچ حوزه‌ای انتخاب نشده است")

    unknown = [key for key in keys if key not in gen.SECTIONS]
    if unknown:
        raise ValueError(f"حوزه ناشناخته: {unknown}")

    return keys


def prepare_preview(keys):
    live = read_json(LIVE_FILE)
    live_sections = live.get("sections", {})

    # فقط داده‌های حوزه‌های انتخابی وارد فایل آزمایشی می‌شوند.
    seed = {
        "updated": live.get("updated"),
        "note": live.get("note", ""),
        "sections": {
            key: live_sections[key]
            for key in keys if key in live_sections
        }
    }

    PREVIEW_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PREVIEW_FILE.open("w", encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False, indent=2)


def validate_preview(keys):
    data = read_json(PREVIEW_FILE)
    sections = data.get("sections")

    if not isinstance(sections, dict):
        raise ValueError("ساختار sections معتبر نیست")

    errors = []
    for key in keys:
        section = sections.get(key)
        if not isinstance(section, dict):
            errors.append(f"{key}: حوزه در خروجی وجود ندارد")
            continue

        if section.get("ok") is not True:
            errors.append(
                f"{key}: تولید ناموفق؛ {section.get('error', 'خطای نامشخص')}"
            )
            continue

        tabs = gen.SECTIONS[key][1]
        run_date = str(data.get("updated", ""))[:10]
        items = [
            item for item in section.get("items", [])
            if isinstance(item, dict) and item.get("date") == run_date
        ]

        counts = {tab: 0 for tab in tabs}
        for item in items:
            if not isinstance(item, dict):
                continue
            tab = item.get("tab")
            if tab in counts:
                counts[tab] += 1

            if not isinstance(item.get("title"), str) or not item["title"].strip():
                errors.append(f"{key}: عنوان خالی")
            if not isinstance(item.get("body"), str) or len(item["body"].strip()) < 60:
                errors.append(f"{key}: متن خالی یا کوتاه")
            script = item.get("short_script")
            if not isinstance(script, list) or len(script) != 3:
                errors.append(f"{key}: short_script باید سه جمله داشته باشد")

        missing = [tab for tab, count in counts.items() if count == 0]
        duplicate = [tab for tab, count in counts.items() if count > 1]

        if missing:
            errors.append(f"{key}: تب‌های بدون مطلب: {missing}")
        if duplicate:
            errors.append(f"{key}: تب‌های دارای مطلب تکراری: {duplicate}")

    if errors:
        raise RuntimeError(
            "Preview validation failed:\n- " + "\n- ".join(errors)
        )

    print("PREVIEW VALIDATION PASSED")
    print("Sections:", ", ".join(keys))
    print("Artifact:", PREVIEW_FILE)


def main():
    keys = selected_sections()
    print("Metatya Preview:", ", ".join(keys))

    prepare_preview(keys)

    # تاریخچه کامل زنده برای dedupe؛ خروجی همچنان آزمایشی است.
    os.environ["HISTORY_FILE"] = str(LIVE_FILE)
    os.environ["CONTENT_OUTPUT"] = str(PREVIEW_FILE)

    gen.OUT = PREVIEW_FILE
    gen.HISTORY_FILE = LIVE_FILE
    gen.SECTIONS = {
        key: gen.SECTIONS[key] for key in keys
    }

    gen.main()
    validate_preview(keys)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PREVIEW FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
