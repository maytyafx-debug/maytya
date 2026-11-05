
"""
Metatya publication gate.

Validates staged content for all configured sections.
The live content file is replaced only after every check passes.
"""

import argparse
import json
import os
import re
import sys
import tempfile
import datetime
from pathlib import Path

from sections import SECTIONS


BANNED = [
    "سود تضمینی",
    "تضمین سود",
    "بدون ریسک",
    "قطعاً سود",
    "قطعا سود",
    "درآمد تضمینی",
]

FINANCIAL_SECTIONS = {
    "forex",
    "crypto",
    "bourse",
    "income",
    "business",
    "finance",
}

DISCLAIMERS = {
    "forex": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "crypto": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "bourse": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "income": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "business": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "finance": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "law": "این مطلب اطلاعات عمومی است و جایگزین مشاوره حقوقی نیست.",
}


def normalize(value):
    value = str(value or "").strip()
    value = value.replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"[\s‌ـ]+", "", value)


def read_json(path):
    if not path.exists():
        raise FileNotFoundError(f"فایل پیدا نشد: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def collect_titles(data):
    titles = set()

    for section in data.get("sections", {}).values():
        if not isinstance(section, dict):
            continue

        for item in section.get("items", []):
            if isinstance(item, dict) and item.get("title"):
                titles.add(normalize(item["title"]))

    return titles


def validate_item(key, item, baseline_titles, seen_titles, today):
    errors = []

    if not isinstance(item, dict):
        return ["ساختار مطلب معتبر نیست."]

    title = str(item.get("title") or "").strip()
    body = str(item.get("body") or "").strip()
    tab = str(item.get("tab") or "").strip()
    provider = str(item.get("provider") or "").strip()
    script = item.get("short_script")

    if not title:
        errors.append("عنوان خالی است.")

    if not 60 <= len(body) <= 1200:
        errors.append("طول متن باید بین ۶۰ تا ۱۲۰۰ نویسه باشد.")

    if not tab:
        errors.append("تب مطلب مشخص نشده است.")

    if not provider:
        errors.append("منبع تولید محتوا مشخص نیست.")

    if item.get("date") != today:
        errors.append("تاریخ مطلب جدید معتبر نیست.")

    if not isinstance(script, list) or len(script) != 3:
        errors.append("short_script باید دقیقاً سه جمله داشته باشد.")
    elif not all(
        isinstance(sentence, str) and 3 <= len(sentence.strip()) <= 120
        for sentence in script
    ):
        errors.append("جمله‌های short_script معتبر نیستند.")

    combined = title + " " + body

    for phrase in BANNED:
        if phrase in combined:
            errors.append(f"عبارت ممنوع یافت شد: {phrase}")

    required_disclaimer = DISCLAIMERS.get(key)

    if required_disclaimer and required_disclaimer not in body:
        errors.append("متن هشدار و سلب مسئولیت حوزه وجود ندارد.")

    normalized_title = normalize(title)

    if normalized_title in baseline_titles:
        errors.append("عنوان با محتوای قبلی تکراری است.")

    if normalized_title in seen_titles:
        errors.append("عنوان در محتوای جدید تکراری است.")

    return errors


def validate(live_data, staged_data):
    errors = []

    live_sections = live_data.get("sections", {})
    staged_sections = staged_data.get("sections", {})

    if not isinstance(staged_sections, dict):
        raise ValueError("ساختار sections در خروجی معتبر نیست.")

    expected_keys = set(SECTIONS)
    actual_keys = set(staged_sections)

    missing_sections = expected_keys - actual_keys
    unexpected_sections = actual_keys - expected_keys

    if missing_sections:
        errors.append(
            "حوزه‌های غایب: " + ", ".join(sorted(missing_sections))
        )

    if unexpected_sections:
        errors.append(
            "حوزه‌های ناشناخته: " + ", ".join(sorted(unexpected_sections))
        )

    baseline_titles = collect_titles(live_data)
    seen_titles = set()

    today = datetime.datetime.now(
        datetime.timezone.utc
    ).date().isoformat()

    total_new = 0

    for key, (section_name, tabs, _needs_web) in SECTIONS.items():
        section = staged_sections.get(key)

        if not isinstance(section, dict):
            errors.append(f"{key}: ساختار حوزه معتبر نیست.")
            continue

        if section.get("ok") is not True:
            errors.append(
                f"{key}: تولید محتوا موفق نبوده است. "
                f"{section.get('error', 'خطای نامشخص')}"
            )
            continue

        items = section.get("items", [])

        if not isinstance(items, list):
            errors.append(f"{key}: فهرست مطالب معتبر نیست.")
            continue

        if section.get("name") != section_name:
            errors.append(f"{key}: نام حوزه با تنظیمات اصلی مطابقت ندارد.")

        new_items = []

        for item in items:
            if not isinstance(item, dict):
                continue

            title = normalize(item.get("title", ""))

            if not title:
                continue

            if title in baseline_titles:
                continue

            if item.get("date") == today:
                new_items.append(item)

        tab_counts = {tab: 0 for tab in tabs}

        for item in new_items:
            total_new += 1

            tab = item.get("tab")

            if tab not in tab_counts:
                errors.append(
                    f"{key}: تب ناشناخته در مطلب جدید: {tab}"
                )
            else:
                tab_counts[tab] += 1

            item_errors = validate_item(
                key,
                item,
                baseline_titles,
                seen_titles,
                today,
            )

            for error in item_errors:
                errors.append(f"{key}: {error}")

            title = normalize(item.get("title", ""))

            if title:
                seen_titles.add(title)

        for tab, count in tab_counts.items():
            if count != 1:
                errors.append(
                    f"{key}: تب «{tab}» باید دقیقاً یک مطلب جدید داشته باشد؛ "
                    f"تعداد فعلی: {count}"
                )

    if total_new == 0:
        errors.append("هیچ محتوای جدیدی برای انتشار وجود ندارد.")

    return errors, total_new


def atomic_promote(staged_path, live_path):
    live_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None

    try:
        with staged_path.open("rb") as source:
            content = source.read()

        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=live_path.parent,
            prefix=".content-",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        os.replace(temp_path, live_path)

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--live", required=True)
    parser.add_argument("--staged", required=True)
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Replace live content only after successful validation.",
    )

    args = parser.parse_args()

    live_path = Path(args.live)
    staged_path = Path(args.staged)

    print("شروع اعتبارسنجی انتشار Metatya...")

    live_data = read_json(live_path)
    staged_data = read_json(staged_path)

    errors, total_new = validate(live_data, staged_data)

    if errors:
        print("\n❌ انتشار متوقف شد.")

        for error in errors:
            print(f"- {error}")

        print("\nنسخه زنده محتوا تغییر نکرد.")
        raise SystemExit(1)

    print("\n✅ اعتبارسنجی موفق بود.")
    print(f"تعداد حوزه‌ها: {len(SECTIONS)}")
    print(f"تعداد مطالب جدید معتبر: {total_new}")

    if args.promote:
        atomic_promote(staged_path, live_path)
        print("\n✅ نسخه معتبر با موفقیت جایگزین محتوای زنده شد.")
    else:
        print("\nحالت بررسی فعال است؛ نسخه زنده تغییر نکرد.")


if __name__ == "__main__":
    main()

