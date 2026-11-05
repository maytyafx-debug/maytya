
"""
Metatya publication gate.

Each configured section is validated independently.
Valid sections are promoted together; failed sections retain their live content.
If no section passes, the live content file remains unchanged.
"""

import argparse
import datetime
import json
import os
import re
import sys
import tempfile
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

DISCLAIMERS = {
    "forex": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "crypto": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "bourse": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "income": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "business": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "finance": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "law": "این مطلب اطلاعات عمومی است و جایگزین مشاوره حقوقی نیست.",
    "sport": "این محتوا عمومی است و جایگزین نظر متخصص سلامت نیست.",
    "health": "این محتوا عمومی است و جایگزین نظر متخصص سلامت نیست.",
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
    sections = data.get("sections", {})

    if not isinstance(sections, dict):
        return titles

    for section in sections.values():
        if not isinstance(section, dict):
            continue

        items = section.get("items", [])

        if not isinstance(items, list):
            continue

        for item in items:
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
        isinstance(sentence, str)
        and 3 <= len(sentence.strip()) <= 120
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

    if normalized_title and normalized_title in baseline_titles:
        errors.append("عنوان با محتوای قبلی تکراری است.")

    if normalized_title and normalized_title in seen_titles:
        errors.append("عنوان در محتوای جدید تکراری است.")

    return errors


def validate_section(
    key,
    section_name,
    tabs,
    staged_section,
    baseline_titles,
    globally_seen_titles,
    today,
):
    errors = []

    if not isinstance(staged_section, dict):
        return ["ساختار حوزه در خروجی جدید معتبر نیست."], 0

    if staged_section.get("ok") is not True:
        reason = staged_section.get("error") or "خطای نامشخص"
        return [f"تولید محتوا موفق نبوده است: {reason}"], 0

    if staged_section.get("name") != section_name:
        errors.append("نام حوزه با تنظیمات اصلی مطابقت ندارد.")

    items = staged_section.get("items", [])

    if not isinstance(items, list):
        return errors + ["فهرست مطالب معتبر نیست."], 0

    new_items = []

    for item in items:
        if not isinstance(item, dict):
            continue

        if item.get("date") != today:
            continue

        title = normalize(item.get("title", ""))

        # Items already present in the live file are historical content,
        # even if their date happens to be today.
        if title and title in baseline_titles:
            continue

        new_items.append(item)

    tab_counts = {tab: 0 for tab in tabs}
    section_seen_titles = set(globally_seen_titles)

    for item in new_items:
        tab = item.get("tab")

        if tab not in tab_counts:
            errors.append(f"تب ناشناخته در مطلب جدید: {tab}")
        else:
            tab_counts[tab] += 1

        item_errors = validate_item(
            key,
            item,
            baseline_titles,
            section_seen_titles,
            today,
        )

        for error in item_errors:
            errors.append(error)

        title = normalize(item.get("title", ""))

        if title:
            section_seen_titles.add(title)

    for tab, count in tab_counts.items():
        if count != 1:
            errors.append(
                f"تب «{tab}» باید دقیقاً یک مطلب جدید داشته باشد؛ "
                f"تعداد فعلی: {count}"
            )

    if not new_items:
        errors.append("هیچ مطلب جدیدی برای این حوزه پیدا نشد.")

    # Only successful sections reserve their titles globally.
    if not errors:
        globally_seen_titles.update(section_seen_titles)

    return errors, len(new_items)


def validate_all(live_data, staged_data):
    live_sections = live_data.get("sections", {})
    staged_sections = staged_data.get("sections", {})

    if not isinstance(live_sections, dict):
        raise ValueError("ساختار sections در فایل زنده معتبر نیست.")

    if not isinstance(staged_sections, dict):
        raise ValueError("ساختار sections در خروجی جدید معتبر نیست.")

    expected_keys = set(SECTIONS)
    actual_keys = set(staged_sections)

    missing_sections = expected_keys - actual_keys
    unexpected_sections = actual_keys - expected_keys

    baseline_titles = collect_titles(live_data)
    globally_seen_titles = set()
    today = datetime.datetime.now(
        datetime.timezone.utc
    ).date().isoformat()

    valid_sections = {}
    failed_sections = {}
    total_new = 0

    for key, (section_name, tabs, _needs_web) in SECTIONS.items():
        staged_section = staged_sections.get(key)

        errors, new_count = validate_section(
            key=key,
            section_name=section_name,
            tabs=tabs,
            staged_section=staged_section,
            baseline_titles=baseline_titles,
            globally_seen_titles=globally_seen_titles,
            today=today,
        )

        if errors:
            failed_sections[key] = errors
        else:
            valid_sections[key] = staged_section
            total_new += new_count

    for key in sorted(missing_sections):
        failed_sections.setdefault(
            key,
            ["این حوزه در خروجی جدید وجود ندارد."],
        )

    for key in sorted(unexpected_sections):
        print(f"WARNING: حوزه ناشناخته نادیده گرفته شد: {key}")

    return {
        "valid_sections": valid_sections,
        "failed_sections": failed_sections,
        "total_new": total_new,
        "today": today,
    }


def atomic_write_json(data, live_path):
    live_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=live_path.parent,
            prefix=".content-",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            json.dump(
                data,
                temp_file,
                ensure_ascii=False,
                indent=2,
            )
            temp_file.write("\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        os.replace(temp_path, live_path)

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def build_merged_content(live_data, staged_data, report):
    merged = dict(live_data)
    merged_sections = dict(live_data.get("sections", {}))

    for key, section in report["valid_sections"].items():
        merged_sections[key] = section

    merged["sections"] = merged_sections

    # Keep the original live metadata if nothing was promoted.
    if report["valid_sections"]:
        if staged_data.get("updated"):
            merged["updated"] = staged_data["updated"]

        merged["publication"] = {
            "mode": "partial",
            "published_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(timespec="seconds"),
            "published_domains": sorted(report["valid_sections"]),
            "retained_domains": sorted(report["failed_sections"]),
            "published_count": len(report["valid_sections"]),
            "retained_count": len(report["failed_sections"]),
            "new_items": report["total_new"],
        }

    return merged


def print_report(report):
    valid = report["valid_sections"]
    failed = report["failed_sections"]

    print("\n" + "=" * 55)
    print("گزارش اعتبارسنجی انتشار Metatya")
    print("=" * 55)

    print(
        f"\nحوزه‌های تأییدشده: "
        f"{len(valid)} از {len(SECTIONS)}"
    )

    for key in sorted(valid):
        print(f"  OK  {key}")

    print(
        f"\nحوزه‌های ناموفق و حفظ‌شده: "
        f"{len(failed)}"
    )

    for key in sorted(failed):
        print(f"\n  FAIL  {key}")

        for error in failed[key]:
            print(f"      - {error}")

    print(f"\nمطالب جدید قابل انتشار: {report['total_new']}")
    print("=" * 55)


def main():
    parser = argparse.ArgumentParser(
        description="Metatya partial content publication gate"
    )

    parser.add_argument("--live", required=True)
    parser.add_argument("--staged", required=True)
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Publish valid sections while retaining failed sections.",
    )

    args = parser.parse_args()

    live_path = Path(args.live)
    staged_path = Path(args.staged)

    print("شروع اعتبارسنجی مستقل حوزه‌های Metatya...")

    live_data = read_json(live_path)
    staged_data = read_json(staged_path)

    report = validate_all(live_data, staged_data)
    print_report(report)

    if not report["valid_sections"]:
        print("\nانتشار متوقف شد؛ هیچ حوزه‌ای تأیید نشد.")
        print("نسخه زنده محتوا بدون تغییر باقی ماند.")
        raise SystemExit(1)

    if args.promote:
        merged_data = build_merged_content(
            live_data,
            staged_data,
            report,
        )

        atomic_write_json(merged_data, live_path)

        print("\nانتشار جزئی با موفقیت انجام شد.")
        print(
            f"{len(report['valid_sections'])} حوزه جدید منتشر شد؛ "
            f"{len(report['failed_sections'])} حوزه قبلی حفظ شد."
        )
    else:
        print("\nحالت بررسی فعال است؛ نسخه زنده تغییر نکرد.")
        print("برای انتشار، گزینه --promote را اجرا کنید.")


if __name__ == "__main__":
    main()
