"""
Metate_bot — نسخه‌ی وب‌هوک، مخصوص هاست رایگان Render
به‌جای polling دائمی، یه سرور وب کوچیک بالا میاد که:
  - آپدیت‌های تلگرام (مثل تاییدیه دکمه‌ها) رو از مسیر /webhook/<SECRET> می‌گیره
  - با یه کرون رایگان بیرونی (cron-job.org) هر روز ساعت ۶ صبح تهران
    مسیر /trigger-daily/<SECRET> رو صدا می‌زنیم تا پست بسازه

راه‌اندازی کامل در README.md
"""

import os
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import feedparser
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup

# ---------------------------------------------------------------------------
# تنظیمات — در پنل Render به‌عنوان Environment Variable وارد می‌کنی
# ---------------------------------------------------------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@maytya")
MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]  # رایگان، از https://console.mistral.ai
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]  # یه رشته رندوم دلخواه بساز، مثل یه پسورد بلند
MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
TEHRAN_TZ = ZoneInfo("Asia/Tehran")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("metate_bot")

flask_app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

DRAFT_PREFIX = "📝 پیش‌نویس پست امروز:\n\n"

# ---------------------------------------------------------------------------
# منابع خبری — فیدهای RSS. هرکدوم رو دوست نداری عوض/اضافه کن.
# ---------------------------------------------------------------------------
RSS_SOURCES = {
    "فارکس و طلا": [
        "https://www.fxstreet.com/rss/news",
        "https://www.investing.com/rss/news_285.rss",
        "https://www.investing.com/rss/commodities_Gold.rss",
    ],
    "کریپتو (بیت‌کوین و اتریوم)": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
    ],
    "بورس ایران": [
        "https://www.tsetmc.com/rss",
        "https://donya-e-eqtesad.com/rss",
    ],
}
MAX_ITEMS_PER_SOURCE = 4


def fetch_news() -> str:
    blocks = []
    for category, urls in RSS_SOURCES.items():
        items = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", "").strip()
                    if title:
                        items.append(f"- {title}: {summary[:200]}")
            except Exception as e:
                logger.warning(f"خطا در خواندن فید {url}: {e}")
        if items:
            blocks.append(f"### {category}\n" + "\n".join(items))
    return "\n\n".join(blocks) if blocks else ""


# ---------------------------------------------------------------------------
# تولید محتوا با Claude
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """تو ویراستار ارشد یک کانال تحلیل بازارهای مالی فارسی‌زبان هستی (@maytya).
با توجه به خبرهای خام ورودی، یک پست روزانه‌ی خفن و خوانا برای تلگرام بساز که دقیقاً این ۴ بخش رو داشته باشه:

🟢 تحلیل فاندامنتال
📊 تحلیل تکنیکال (طلا، فارکس، بیت‌کوین، اتریوم، بورس ایران - هرکدوم خبر داشت)
🧠 روانشناسی بازار
🛡 مدیریت ریسک و سرمایه

قوانین:
- لحن حرفه‌ای ولی جذاب و خودمونی، با ایموجی مناسب (نه زیاد)
- هر بخش حداکثر ۴-۵ خط، خلاصه و کاربردی
- در انتها یک خط دیسکلیمر بذار: "این محتوا صرفاً جنبه آموزشی دارد و توصیه سرمایه‌گذاری نیست."
- تاریخ شمسی امروز رو در ابتدای پست بنویس
- فقط خروجی نهایی پست رو بده، بدون توضیح اضافه یا مقدمه"""


def generate_content(raw_news: str) -> str:
    today = datetime.now(TEHRAN_TZ).strftime("%Y-%m-%d")
    user_prompt = (
        f"تاریخ: {today}\n\nخبرهای خام امروز:\n"
        f"{raw_news if raw_news else '(فیدها خبر جدیدی نداشتند، بر اساس روند کلی اخیر بازار بنویس)'}"
    )
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    resp = requests.post(
        MISTRAL_URL,
        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# فلو تایید — نکته‌ی مهم: چون روی هاست رایگان پروسه ممکنه بین دو درخواست
# خاموش/روشن بشه، هیچ‌چیزی تو حافظه نگه نمی‌داریم. وقتی ادمین دکمه رو می‌زنه،
# خودِ متنِ پیام تلگرام (که دست تلگرامه نه ما) به‌عنوان منبع محتوا استفاده می‌شه.
# ---------------------------------------------------------------------------
async def send_draft_for_approval():
    logger.info("در حال تهیه محتوای روزانه...")
    try:
        raw_news = fetch_news()
        content = generate_content(raw_news)
    except Exception as e:
        logger.exception("خطا در تولید محتوا")
        await bot.send_message(ADMIN_CHAT_ID, f"⚠️ خطا در تولید محتوای روزانه: {e}")
        return

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ تایید و انتشار", callback_data="approve"),
        InlineKeyboardButton("❌ رد", callback_data="reject"),
    ]])
    await bot.send_message(ADMIN_CHAT_ID, DRAFT_PREFIX + content, reply_markup=keyboard)


async def handle_update(update: Update):
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        if q.from_user.id != ADMIN_CHAT_ID:
            return
        text = q.message.text or ""
        content = text[len(DRAFT_PREFIX):] if text.startswith(DRAFT_PREFIX) else text
        if q.data == "approve":
            await bot.send_message(CHANNEL_ID, content)
            await q.edit_message_text("✅ منتشر شد در کانال @" + CHANNEL_ID.lstrip("@"))
        else:
            await q.edit_message_text("❌ رد شد و منتشر نشد.")
    elif update.message and update.message.text:
        if update.message.chat_id == ADMIN_CHAT_ID and update.message.text.strip() == "/generate":
            await bot.send_message(ADMIN_CHAT_ID, "⏳ در حال تهیه پست...")
            await send_draft_for_approval()


# ---------------------------------------------------------------------------
# مسیرهای وب
# ---------------------------------------------------------------------------
@flask_app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    asyncio.run(handle_update(update))
    return "ok"


@flask_app.route(f"/trigger-daily/{WEBHOOK_SECRET}", methods=["GET"])
def trigger_daily():
    asyncio.run(send_draft_for_approval())
    return "triggered"


@flask_app.route("/")
def health():
    return "Metate_bot is alive ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
