"""اجرای آزمایشی تولید محتوا برای Metatya
- فایل زنده docs/content.json را تغییر نمی‌دهد.
- خروجی فقط در out/preview-content.json ذخیره می‌شود.
- به‌صورت پیش‌فرض فقط forex و crypto را اجرا می‌کند.
- در صورت شکست هر حوزه یا ناقص بودن تب‌ها، با کد خطا خارج می‌شود.
"""

import json
import os
import sys
from pathlib import Path

# مسیر ریشه مخزن
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
OUT_DIR = ROOT / "out"
PREVIEW_FILE = OUT_DIR / "preview-content.json"
LIVE_FILE = ROOT / "docs" / "content.json"

# برای import صحیح generate.py
sys.path.insert(0, str(SCRIPTS))

import generate as gen


def selected_sections():
    raw = os.getenv("PREVIEW_SECTIONS", "forex,crypto")
    selected = [item.strip() for item in raw.split(",") if item.strip()]

    if not selected:
        raise ValueError("هیچ حوزه‌ای برای پیش‌نمایش انتخاب نشده است.")

    unknown = [key for key in selected if key not in gen.SECTIONS]
    if unknown:
        raise ValueError(f"حوزه‌های ناشناخته: {unknown}")

    # حذف موارد تکراری، با حفظ ترتیب
    return list(dict.fromkeys(selected))


def prepare_preview_seed(keys):
    """فقط داده‌های قبلی حوزه‌های انتخاب‌شده را به فایل پیش‌نمایش منتقل می‌کند."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not LIVE_FILE.exists():
        seed = {"sections": {}}
    else:
        with LIVE_FILE.open("r", encoding="utf-8") as file:
            live_data = json.load(file)

        live_sections = live_data.get("sections", {})
        seed = {
            "updated": live_data.get("updated"),
            "note": live_data.get("note", ""),
            "sections": {
                key: live_sections[key]
                for key in keys
                if key in live_sections
            },
        }

    with PREVIEW_FILE.open("w", encoding="utf-8") as file:
        json.dump(seed, file, ensure_ascii=False, indent=2)


def validate_preview(keys):
    if not PREVIEW_FILE.exists():
        raise RuntimeError("فایل پیش‌نمایش ساخته نشده است.")

    with PREVIEW_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    sections = data.get("sections")
    if not isinstance(sections, dict):
        raise ValueError("ساختار sections در خروجی معتبر نیست.")

    errors = []

    for key in keys:
        if key not in sections:
            errors.append(f"{key}: حوزه در خروجی وجود ندارد.")
            continue

        section = sections[key]
        expected_tabs = gen.SECTIONS[key][1]

        if section.get("ok") is not True:
            errors.append(
                f"{key}: تولید ناموفق؛ {section.get('error', 'خطای نامشخص')}"
            )
            continue

        items = section.get("items", [])
        new_items = [
            item for item in items
            if isinstance(item, dict) and item.get("date") == data.get("updated", "")[:10]
        ]

        # بررسی محتوای تولیدشده در اجرای فعلی
        tab_counts = {tab: 0 for tab in expected_tabs}

        for item in new_items:
            tab = item.get("tab")
            if tab in tab_counts:
                tab_counts[tab] += 1

            if not isinstance(item.get("title"), str) or not item["title"].strip():
                errors.append(f"{key}: عنوان خالی یا نامعتبر است.")

            if not isinstance(item.get("body"), str) or not item["body"].strip():
                errors.append(f"{key}: متن خالی یا نامعتبر است.")

            script = item.get("short_script")
            if not isinstance(script, list) or len(script) != 3:
                errors.append(f"{key}: short_script باید دقیقاً سه جمله داشته باشد.")

        missing = [tab for tab, count in tab_counts.items() if count == 0]
        duplicated = [tab for tab, count in tab_counts.items() if count > 1]

        if missing:
            errors.append(f"{key}: تب‌های بدون محتوای تازه: {missing}")

        if duplicated:
            errors.append(f"{key}: تب‌های تکراری: {duplicated}")

    if errors:
        raise RuntimeError(
            "اعتبارسنجی پیش‌نمایش ناموفق بود:\n- " + "\n- ".join(errors)
        )

    print("اعتبارسنجی موفق بود.")
    print(f"حوزه‌های بررسی‌شده: {', '.join(keys)}")
    print(f"فایل خروجی: {PREVIEW_FILE}")


def main():
    if not os.getenv("OPENROUTER_API_KEY", "").strip():
        raise RuntimeError(
            "کلید OPENROUTER_API_KEY در محیط اجرا تنظیم نشده است."
        )

    keys = selected_sections()

    print("Metatya Preview Generator")
    print("حوزه‌ها:", ", ".join(keys))

    # ابتدا محتوای قبلی فقط به فایل آزمایشی منتقل می‌شود.
    prepare_preview_seed(keys)

    # تنظیم موتور اصلی روی حالت واقعی، اما با خروجی آزمایشی
    gen.DRY = False
    gen.OUT = str(PREVIEW_FILE)
    gen.SECTIONS = {
        key: gen.SECTIONS[key]
        for key in keys
    }

    # تولید محتوا
    gen.main()

    # موتور اصلی ممکن است با موفقیت نسبی هم برگردد؛
    # بنابراین اعتبارسنجی مستقل ضروری است.
    validate_preview(keys)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"PREVIEW FAILED: {error}", file=sys.stderr)
        sys.exit(1)
    except SystemExit as error:
        # خطاهای خروجی موتور اصلی نیز باید در Actions شکست محسوب شوند.
        if error.code not in (None, 0):
            raise
