
"""Metatya content engine.
Preview-safe, optional OpenRouter, local fallback for forex/crypto.
"""
import os
import sys
import json
import re
import time
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from sections import SECTIONS

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
OUT = Path(os.getenv(
    "CONTENT_OUTPUT",
    str(ROOT / ("out/dry-content.json" if DRY else "docs/content.json"))
))
HISTORY_FILE = Path(os.getenv("HISTORY_FILE", str(OUT)))
KEEP = 40

OR_MODELS_DEFAULT = "xingchen-agi/xing4.0-29b-a4b:free"
OR_URL = "https://openrouter.ai/api/v1/chat/completions"

BANNED = [
    "سود تضمینی", "تضمین سود", "بدون ریسک",
    "قطعاً سود", "قطعا سود", "درآمد تضمینی"
]

MARKET_TABS = ["تکنیکال", "فاندامنتال", "آموزش", "روان‌شناسی"]

DISCLAIMER = {
    "fin": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "med": "این محتوا عمومی است و جایگزین نظر متخصص سلامت نیست.",
    "law": "این مطلب اطلاعات عمومی است و جایگزین مشاوره حقوقی نیست.",
    "general": "این محتوا آموزشی و عمومی است."
}

KIND = {
    "forex": "fin", "crypto": "fin", "bourse": "fin",
    "income": "fin", "business": "fin", "finance": "fin",
    "sport": "med", "health": "med", "law": "law",
    "ai": "general", "privacy": "general"
}

FEEDS = {
    "forex": [
        "https://news.google.com/rss/search?q=forex+EURUSD+dollar+Fed&hl=en-US&gl=US&ceid=US:en"
    ],
    "crypto": [
        "https://news.google.com/rss/search?q=bitcoin+crypto+ETF&hl=en-US&gl=US&ceid=US:en",
        "https://cointelegraph.com/rss"
    ],
    "bourse": [
        "https://news.google.com/rss/search?q=%D8%A8%D9%88%D8%B1%D8%B3+%D8%A7%DB%8C%D8%B1%D8%A7%D9%86&hl=fa&gl=IR&ceid=IR:fa"
    ]
}

PROMPT = """
تو سردبیر آموزشی پلتفرم فارسی Metatya هستی.
حوزه: {name}
تاریخ: {today}
تب‌های مجاز: {tabs}
زمینه خبری: {context}
عنوان‌های اخیر در تمام حوزه‌ها که نباید تکرار شوند:
{history}

برای هر تب دقیقاً یک مطلب تازه و مستقل تولید کن.
عنوان و متن باید فارسی، روشن، مفید و غیرتکراری باشند.
متن هر مطلب ۶۰ تا ۹۰۰ نویسه باشد.
هر مطلب یک مسئله را توضیح دهد و یک نکته آموزشی روشن داشته باشد.
از وعده سود، ادعای قطعی، خبر یا قیمت ساختگی و توصیه شخصی خودداری کن.
اگر خبر کافی نیست، محتوای آموزشی ماندگار بنویس.
برای short_script دقیقاً سه جمله بنویس:
۱) هوک کوتاه
۲) نکته آموزشی
۳) جمع‌بندی یا پرسش مرتبط

برای بازارهای مالی فقط آموزش عمومی، سواد مالی و مدیریت ریسک؛
بدون سیگنال، نقطه ورود یا خروج و پیش‌بینی قطعی.

فقط JSON معتبر با این ساختار برگردان:
{{"items":[
 {{"tab":"نام تب","title":"عنوان","body":"متن","short_script":["هوک","نکته","جمع‌بندی"]}}
]}}
"""


# محتوای محلی مستقل از API؛ فعلاً فقط برای دو حوزه Preview
LOCAL_BANK = {
    "forex": {
        "تکنیکال": [
            ("ساختار بازار را قبل از اندیکاتور بشناس",
             "در بررسی نمودار، ابتدا به توالی سقف‌ها و کف‌ها توجه کن. این ساختار تصویری ساده از رفتار قیمت در بازه انتخابی می‌دهد؛ اما به‌تنهایی جهت آینده را مشخص نمی‌کند. اندیکاتورها ابزار کمکی‌اند و نباید جای مشاهده و ثبت شواهد را بگیرند. برای یادگیری، چند نمودار تاریخی را بدون پیش‌بینی نتیجه بررسی و مشاهداتت را ثبت کن."),
            ("حمایت و مقاومت؛ ناحیه‌اند نه عدد جادویی",
             "سطوح حمایت و مقاومت بهتر است به‌صورت ناحیه بررسی شوند، نه یک قیمت دقیق و قطعی. واکنش‌های گذشته می‌توانند محل توجه معامله‌گران را نشان دهند، اما تضمینی برای تکرار رفتار بازار نیستند. در تمرین نموداری، محدوده‌ها را مشخص کن و سپس بررسی کن آیا واکنش قیمت با فرض اولیه‌ات سازگار بوده است یا نه.")
        ],
        "فاندامنتال": [
            ("نرخ بهره چرا در بازار ارز اهمیت دارد؟",
             "نرخ بهره بر هزینه نگهداری پول و جذابیت نسبی دارایی‌ها اثر می‌گذارد. بااین‌حال، واکنش ارزها فقط به یک عدد وابسته نیست؛ انتظارات قبلی، لحن بانک مرکزی و داده‌های اقتصادی دیگر نیز اهمیت دارند. هنگام مطالعه یک تصمیم پولی، تفاوت میان انتظار بازار و نتیجه اعلام‌شده را یادداشت کن و از نتیجه‌گیری قطعی درباره جهت قیمت پرهیز کن."),
            ("تورم را جدا از انتظارات بازار بررسی کن",
             "انتشار داده تورم به‌تنهایی تصویر کاملی از شرایط اقتصادی نمی‌دهد. بازار ممکن است پیش از انتشار، بخشی از انتظار خود را در قیمت‌ها منعکس کرده باشد. برای تحلیل آموزشی، عدد اعلام‌شده را کنار مقدار قبلی و پیش‌بینی منتشرشده قرار بده و محدودیت این مقایسه را هم بنویس. یک داده اقتصادی به‌تنهایی مبنای تصمیم قطعی نیست.")
        ],
        "آموزش": [
            ("دفتر ثبت معاملات چه چیزی را آشکار می‌کند؟",
             "حافظه انسان معمولاً جزئیات تصمیم‌های گذشته را دقیق نگه نمی‌دارد. ثبت دلیل تصمیم، شرایط بازار، میزان ریسک برنامه‌ریزی‌شده و نتیجه مشاهده‌شده کمک می‌کند الگوهای رفتاری را بهتر بشناسی. دفتر ثبت قرار نیست نتیجه را تضمین کند؛ ارزش آن در تبدیل تجربه‌های پراکنده به داده قابل بررسی است. مرور منظم یادداشت‌ها، کیفیت فرایند یادگیری را بهتر می‌کند."),
            ("تفاوت ریسک هر معامله با ریسک کل حساب",
             "ریسک یک موقعیت فقط بخشی از تصویر است. چند موقعیت هم‌جهت یا دارایی‌های به‌شدت هم‌بسته می‌توانند در عمل ریسک مشترکی ایجاد کنند. در آموزش مدیریت ریسک، علاوه بر هر موقعیت، مجموع مواجهه‌ها و سناریوی زیان هم‌زمان را بررسی کن. هدف این است که وابستگی میان تصمیم‌ها دیده شود، نه اینکه فقط هر مورد جداگانه ارزیابی شود.")
        ],
        "روان‌شناسی": [
            ("چرا تصمیم عجولانه بعد از زیان رخ می‌دهد؟",
             "پس از یک نتیجه نامطلوب، ممکن است فرد برای جبران سریع، قواعد قبلی خود را کنار بگذارد. این واکنش می‌تواند کیفیت ارزیابی را کاهش دهد. ثبت احساس پیش و پس از تصمیم، مکث و مرور چک‌لیست از روش‌های آموزشی برای شناخت این الگو هستند. هدف، حذف کامل احساسات نیست؛ هدف این است که احساس جایگزین فرایند سنجیده نشود."),
            ("اعتمادبه‌نفس را با قطعیت اشتباه نگیر",
             "تجربه بیشتر می‌تواند مهارت ارزیابی را تقویت کند، اما هیچ فردی از خطا مصون نیست. وقتی فرضیه‌ای با شواهد مخالف روبه‌رو می‌شود، توانایی بازبینی آن نشانه تفکر نقادانه است. در دفتر یادداشت، شواهد موافق و مخالف را جدا بنویس و میزان اطمینانت را نیز ثبت کن. این کار کمک می‌کند تفاوت میان باور و واقعیت روشن‌تر شود.")
        ]
    },
    "crypto": {
        "تکنیکال": [
            ("نوسان بالا، اهمیت اندازه‌گیری را بیشتر می‌کند",
             "بازار رمزارزها ممکن است در بازه‌های کوتاه نوسان قابل‌توجهی داشته باشد. به همین دلیل، مشاهده نمودار بدون توجه به بازه زمانی و مقیاس می‌تواند برداشت نادرستی ایجاد کند. هنگام مطالعه نمودار، تایم‌فریم، دامنه تغییرات و حجم معاملات را کنار هم ثبت کن. هیچ‌کدام به‌تنهایی جهت آینده را تضمین نمی‌کنند."),
            ("حجم معاملات را در کنار قیمت بخوان",
             "تغییر قیمت بدون بررسی حجم، اطلاعات ناقصی ارائه می‌کند. حجم می‌تواند نشان دهد در یک بازه چه میزان فعالیت ثبت شده است، اما تفسیر آن به نوع بازار و کیفیت داده وابسته است. برای تمرین، چند حرکت تاریخی را با حجم همان بازه مقایسه کن و مواردی را که داده ناقص یا غیرعادی دارند جدا علامت بزن.")
        ],
        "فاندامنتال": [
            ("عرضه یک رمزارز را چگونه ارزیابی کنیم؟",
             "برای شناخت یک دارایی دیجیتال، فقط قیمت روز کافی نیست. عرضه در گردش، سقف عرضه اعلام‌شده، برنامه آزادسازی توکن‌ها و تمرکز مالکیت می‌توانند در ارزیابی ساختار آن مؤثر باشند. این داده‌ها باید از مستندات معتبر همان پروژه بررسی شوند؛ زیرا تعریف عرضه در پروژه‌های مختلف یکسان نیست. هیچ شاخصی به‌تنهایی ارزش آینده را مشخص نمی‌کند."),
            ("کاربرد واقعی پروژه را از تبلیغات جدا کن",
             "وعده‌های بازاریابی لزوماً نشان‌دهنده استفاده واقعی از یک شبکه نیستند. برای ارزیابی آموزشی، مسئله‌ای را که پروژه ادعا می‌کند حل می‌کند، کاربران هدف، مستندات فنی و شواهد استفاده را جداگانه بررسی کن. اگر داده مستقل یا قابل راستی‌آزمایی وجود ندارد، آن را به‌عنوان ابهام ثبت کن؛ نه اینکه ادعا را واقعیت قطعی فرض کنی.")
        ],
        "آموزش": [
            ("کیف پول امانی و غیرامانی چه تفاوتی دارند؟",
             "در کیف پول امانی، نگهداری کلیدها معمولاً بر عهده یک ارائه‌دهنده خدمت است. در کیف پول غیرامانی، کنترل کلید خصوصی در اختیار خود کاربر قرار می‌گیرد و مسئولیت حفاظت از آن نیز بیشتر بر عهده اوست. پیش از استفاده از هر ابزار، سازوکار بازیابی، پشتیبانی و خطرهای آن را از مستندات رسمی بررسی کن. عبارت بازیابی را با هیچ‌کس به اشتراک نگذار."),
            ("کارمزد شبکه را با کارمزد صرافی یکی ندان",
             "در انتقال دارایی دیجیتال ممکن است هزینه شبکه و هزینه خدمات پلتفرم با هم متفاوت باشند. مقدار کارمزد شبکه به ازدحام و سازوکار همان شبکه وابسته است؛ درحالی‌که پلتفرم ممکن است هزینه جداگانه‌ای داشته باشد. پیش از هر انتقال واقعی، اطلاعات رسمی و مبلغ نهایی نمایش‌داده‌شده را با دقت بررسی کن و تفاوت این دو هزینه را بشناس.")
        ],
        "روان‌شناسی": [
            ("ترس از جا ماندن چگونه قضاوت را مختل می‌کند؟",
             "دیدن رشد سریع یک دارایی ممکن است احساس جا ماندن از فرصت را ایجاد کند. این احساس می‌تواند فرد را به تصمیم عجولانه وادار کند، حتی وقتی اطلاعات کافی ندارد. برای شناخت این الگو، پیش از هر ارزیابی فرضیه، شواهد و موارد نامعلوم را بنویس. فرصت ازدست‌رفته، به‌خودی‌خود دلیل مناسبی برای تصمیم تازه نیست."),
            ("اثر جمع را با شواهد مستقل اشتباه نگیر",
             "تکرار یک ادعا در شبکه‌های اجتماعی لزوماً اعتبار آن را بیشتر نمی‌کند. تعداد بازنشرها جایگزین منبع اولیه، داده قابل بررسی یا تحلیل مستقل نیست. هنگام مواجهه با یک روایت پرطرفدار، منبع اصلی را پیدا کن، تاریخ انتشار را بررسی کن و شواهد مخالف را هم بخوان. این عادت از تصمیم‌گیری صرفاً بر پایه هیجان جمعی جلوگیری می‌کند.")
        ]
    }
}


def env(name, default=""):
    return (os.getenv(name) or default).strip()


def normalize(value):
    value = str(value or "").strip()
    value = value.replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"[\s‌ـ]+", "", value)


def read_json(path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def all_recent_titles():
    data = read_json(HISTORY_FILE)
    result = set()
    for section in data.get("sections", {}).values():
        for item in section.get("items", []):
            title = item.get("title")
            if title:
                result.add(normalize(title))
    return result


def get_headlines(key):
    result = []
    for url in FEEDS.get(key, []):
        try:
            response = requests.get(
                url, timeout=12,
                headers={"User-Agent": "Mozilla/5.0 Metatya"}
            )
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for item in root.iter("item"):
                title = (item.findtext("title") or "").strip()
                if title:
                    result.append(title)
                if len(result) >= 15:
                    break
        except Exception as exc:
            print(f"RSS warning [{key}]: {str(exc)[:100]}")
    return result[:15]


def fa_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0
    return sum("\u0600" <= c <= "\u06ff" for c in letters) / len(letters)


def validate_items(items, tabs, key):
    if not isinstance(items, list):
        raise ValueError("items باید آرایه باشد")

    tab_lookup = {normalize(tab): tab for tab in tabs}
    counts = {tab: 0 for tab in tabs}
    clean = []

    for item in items:
        if not isinstance(item, dict):
            continue

        tab = tab_lookup.get(normalize(item.get("tab")))
        title = str(item.get("title") or "").strip()
        body = str(item.get("body") or "").strip()
        script = item.get("short_script")

        if tab is None:
            continue
        if not 5 <= len(title) <= 140:
            continue
        if not 60 <= len(body) <= 900:
            continue
        if fa_ratio(title + body) < 0.55:
            continue
        if any(word in title + body for word in BANNED):
            continue
        if not isinstance(script, list) or len(script) != 3:
            continue
        if not all(isinstance(x, str) and 3 <= len(x) <= 120 for x in script):
            continue

        disclaimer = DISCLAIMER.get(KIND.get(key, "general"), "")
        if disclaimer and disclaimer not in body:
            body += " " + disclaimer

        clean.append({
            "tab": tab,
            "title": title,
            "body": body,
            "short_script": script
        })
        counts[tab] += 1

    missing = [tab for tab, count in counts.items() if count == 0]
    duplicate = [tab for tab, count in counts.items() if count > 1]

    if missing or duplicate:
        raise ValueError(
            f"پوشش تب ناقص است؛ جاافتاده={missing} تکراری={duplicate}"
        )

    return clean


def local_fallback(key, tabs, recent):
    bank = LOCAL_BANK.get(key)
    if not bank:
        raise RuntimeError(
            f"fallback محلی برای حوزه {key} هنوز آماده نشده است"
        )

    output = []
    for tab in tabs:
        candidates = bank.get(tab, [])
        selected = next(
            (entry for entry in candidates
             if normalize(entry[0]) not in recent),
            None
        )
        if not selected:
            raise RuntimeError(
                f"موضوع تازه و بدون تکرار برای {key}/{tab} موجود نیست"
            )

        title, body = selected
        output.append({
            "tab": tab,
            "title": title,
            "body": body,
            "short_script": [
                title,
                "این نکته را با شواهد و منابع معتبر بررسی کن.",
                "برای مرور بعدی، این مطلب را ذخیره کن."
            ],
            "provider": "local-fallback"
        })
        recent.add(normalize(title))

    return validate_items(output, tabs, key)


def call_openrouter(prompt):
    key = env("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("کلید OpenRouter تنظیم نشده است")

    models = [
        x.strip() for x in env("OR_MODELS", OR_MODELS_DEFAULT).split(",")
        if x.strip()
    ]
    if not models:
        raise RuntimeError("فهرست مدل‌ها خالی است")

    last_error = "unknown"
    for model in models:
        payload = {
            "model": model,
            "temperature": 0.35,
            "max_tokens": 5000,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            response = requests.post(
                OR_URL,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://maytyafx-debug.github.io/maytya/",
                    "X-Title": "Metatya"
                },
                json=payload,
                timeout=60
            )

            if response.status_code == 429:
                retry = response.headers.get("Retry-After", "5")
                try:
                    wait = min(max(int(float(retry)), 1), 10)
                except ValueError:
                    wait = 5
                time.sleep(wait)
                response = requests.post(
                    OR_URL,
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://maytyafx-debug.github.io/maytya/",
                        "X-Title": "Metatya"
                    },
                    json=payload,
                    timeout=60
                )

            if response.status_code in (401, 403):
                raise RuntimeError(
                    "کلید OpenRouter معتبر نیست یا دسترسی ندارد"
                )

            response.raise_for_status()
            content = response.json()["choices"][0]["message"].get("content")
            if not content:
                raise ValueError("مدل پاسخ خالی برگرداند")

            match = re.search(r"\{.*\}", content, re.S)
            if not match:
                raise ValueError("JSON در پاسخ مدل پیدا نشد")

            return json.loads(match.group(0)), model

        except Exception as exc:
            last_error = f"{model}: {str(exc)[:160]}"
            print("OpenRouter fallback:", last_error)

    raise RuntimeError(last_error)


def generate_section(key, name, tabs, recent):
    context = get_headlines(key)
    context_text = "\n".join("- " + x for x in context) or (
        "خبر قابل اتکا در دسترس نیست؛ فقط آموزش ماندگار تولید کن."
    )

    history_text = "\n".join(sorted(recent))[-12000:] or "ندارد"
    prompt = PROMPT.format(
        name=name,
        today=datetime.date.today().isoformat(),
        tabs="، ".join(tabs),
        context=context_text,
        history=history_text
    )

    if env("OPENROUTER_API_KEY"):
        try:
            payload, model = call_openrouter(prompt)
            items = validate_items(payload.get("items"), tabs, key)

            for item in items:
                if normalize(item["title"]) in recent:
                    raise ValueError("عنوان تکراری با محتوای اخیر")
            return items, model

        except Exception as exc:
            print(f"AI failed [{key}], using local fallback: {exc}")

    items = local_fallback(key, tabs, recent)
    return items, "local-fallback"


def main():
    old_data = read_json(OUT)
    old_sections = old_data.get("sections", {})
    recent = all_recent_titles()

    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date().isoformat()
    result = {}
    successes = 0

    for key, (name, tabs, _needs_web) in SECTIONS.items():
        previous = old_sections.get(key, {}).get("items", [])
        section_recent = set(recent)

        try:
            items, provider = generate_section(
                key, name, tabs, section_recent
            )

            for item in items:
                item["date"] = today
                item["provider"] = provider
                recent.add(normalize(item["title"]))

            result[key] = {
                "name": name,
                "items": (items + previous)[:KEEP],
                "ok": True,
                "provider": provider
            }
            successes += 1
            print(f"OK {key}: {len(items)} items [{provider}]")

        except Exception as exc:
            result[key] = {
                "name": name,
                "items": previous[:KEEP],
                "ok": False,
                "provider": None,
                "error": str(exc)[:300]
            }
            print(f"FAIL {key}: {exc}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "updated": now.isoformat(timespec="seconds"),
        "note": (
            "محتوای آموزشی عمومی؛ اطلاعات بازار لحظه‌ای نیست و "
            "مطالب جایگزین مشاوره تخصصی نیستند."
        ),
        "sections": result
    }

    with OUT.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"RESULT: {successes}/{len(SECTIONS)} sections succeeded")
    if successes == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
