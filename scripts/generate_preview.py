
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS))

import generate as gen

LIVE_FILE = ROOT / "docs" / "content.json"
PREVIEW_FILE = ROOT / "out" / "preview-content.json"


def read_json(path):
    if not path.exists():
        raise FileNotFoundError(f"فایل پیدا نشد: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def normalize_title(value):
    return gen.normalize(str(value or ""))


def collect_titles(data):
    titles = set()

    sections = data.get("sections", {})

    for section in sections.values():
        if not isinstance(section, dict):
            continue

        for item in section.get("items", []):
            if isinstance(item, dict) and item.get("title"):
                titles.add(normalize_title(item["title"]))

    return titles


def selected_sections():
    raw = os.getenv("PREVIEW_SECTIONS", "forex,crypto")

    keys = [
        item.strip()
        for item in raw.split(",")
        if item.strip()
    ]

    if not keys:
        raise ValueError("هیچ بخشی برای پیش‌نمایش انتخاب نشده است.")

    unknown = [key for key in keys if key not in gen.SECTIONS]

    if unknown:
        raise ValueError(
            "بخش‌های ناشناخته: " + ", ".join(unknown)
        )

    return keys


def prepare_preview(keys):
    live = read_json(LIVE_FILE)

    baseline_titles = collect_titles(live)
    live_sections = live.get("sections", {})

    seed = {
        "updated": live.get("updated"),
        "note": live.get("note", ""),
        "sections": {
            key: live_sections.get(
                key,
                {
                    "title": gen.SECTIONS[key][0],
                    "items": []
                }
            )
            for key in keys
        }
    }

    write_json(PREVIEW_FILE, seed)

    return baseline_titles


def validate_preview(keys, baseline_titles):
    data = read_json(PREVIEW_FILE)
    sections = data.get("sections", {})

    errors = []
    total_new_items = 0

    for key in keys:
        section = sections.get(key)

        if not isinstance(section, dict):
            errors.append(f"{key}: بخش در خروجی وجود ندارد.")
            continue

        items = section.get("items", [])

        if not isinstance(items, list):
            errors.append(f"{key}: فهرست محتوا معتبر نیست.")
            continue

        new_items = []

        for item in items:
            if not isinstance(item, dict):
                continue

            title = normalize_title(item.get("title", ""))

            if title and title not in baseline_titles:
                new_items.append(item)

        expected_tabs = gen.SECTIONS[key][1]
        tab_counts = {tab: 0 for tab in expected_tabs}

        for item in new_items:
            tab = item.get("tab")
            if tab in tab_counts:
                tab_counts[tab] += 1

            for field in ("title", "body", "short_script"):
                value = item.get(field)
                if not value or (isinstance(value, str) and not value.strip()):
                    errors.append(f"{key}: فیلد {field} خالی است.")

            if not item.get("provider"):
                errors.append(f"{key}: منبع تولید ثبت نشده است.")

        missing = [t for t, c in tab_counts.items() if c == 0]
        duplicate = [t for t, c in tab_counts.items() if c > 1]

        if missing:
            errors.append(f"{key}: تب‌های بدون محتوای جدید: {missing}")
        if duplicate:
            errors.append(f"{key}: تب‌های با بیش از یک محتوای جدید: {duplicate}")

        total_new_items += len(new_items)

    if errors:
        print("\n❌ اعتبارسنجی پیش‌نمایش ناموفق بود:")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("\n✅ اعتبارسنجی پیش‌نمایش موفق بود.")
    print(f"تعداد بخش‌های بررسی‌شده: {len(keys)}")
    print(f"تعداد محتوای جدید معتبر: {total_new_items}")
    print(f"فایل خروجی: {PREVIEW_FILE}")


def main():
    keys = selected_sections()

    print("شروع ساخت پیش‌نمایش Metatya...")
    print("بخش‌ها:", ", ".join(keys))

    baseline_titles = prepare_preview(keys)

    os.environ["HISTORY_FILE"] = str(LIVE_FILE)
    os.environ["CONTENT_OUTPUT"] = str(PREVIEW_FILE)

    gen.OUT = PREVIEW_FILE
    gen.HISTORY_FILE = LIVE_FILE

    gen.SECTIONS = {
        key: gen.SECTIONS[key]
        for key in keys
    }

    gen.main()

    validate_preview(keys, baseline_titles)


if __name__ == "__main__":
    main()
