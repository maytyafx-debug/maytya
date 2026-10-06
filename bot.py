"""
Metatya Bot — نسخه وب‌هوک برای Render
راه‌اندازی کامل در README.md
"""
import os
import re
import time
import asyncio
import logging
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import feedparser
import jdatetime
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup

# ---------- تنظیمات ----------
def _env(key, required=True, default=None):
    val = os.environ.get(key, default)
    if required and not val:
        raise SystemExit(f"❌ متغیر محیطی {key} تنظیم نشده")
    return val

BOT_TOKEN       = _env("BOT_TOKEN")
ADMIN_CHAT_ID   = int(_env("ADMIN_CHAT_ID"))
CHANNEL_ID      = os.environ.get("CHANNEL_ID", "@Maytyafx")
MISTRAL_API_KEY = _env("MISTRAL_API_KEY")
WEBHOOK_SECRET  = _env("WEBHOOK_SECRET")
PUBLIC_URL      = _env("PUBLIC_URL")

MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")
MISTRAL_URL   = "https://api.mistral.ai/v1/chat/completions"
TEHRAN_TZ     = ZoneInfo("Asia/Tehran")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("metatya_bot")

flask_app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

DRAFT_PREFIX = "📝 پیش‌نویس پست امروز:\n\n"

# ---------- منابع خبری ----------
RSS_SOURCES = {
    "فارکس و طلا": [
        "https://www.fxstreet.com/rss/news",
        "https://www.investing.com/rss/news_285.rss",
        "https://www.investing.com/rss/commodities_Gold.rss",
    ],
    "کریپتو": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
    ],
    "بورس ایران": [
        "https://donya-e-eqtesad.com/feeds/",
        "https://www.fardanews.com/fa/rss/economic",
    ],
}
MAX_ITEMS_PER_SOURCE = 4


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_news() -> str:
    blocks = []
    for category, urls in RSS_SOURCES.items():
        items = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
                    title = _clean_html(entry.get("title", ""))
                    summary = _clean_html(entry.get("summary", ""))[:200]
                    if title:
                        items.append(f"- {title}: {summary}")
            except Exception as e:
                logger.warning(f"RSS error {url}: {e}")
        if items:
            blocks.append(f"### {category}\n" + "\n".join(items))
    return "\n\n".join(blocks) if blocks else ""


# ---------- تولید محتوا با Mistral ----------
SYSTEM_PROMPT = """تو ویراستار ارشد یک کانال تحلیل بازارهای مالی فارسی‌زبان هستی (@Maytyafx).
با توجه به خبرهای خام ورودی، یک پست روزانه بساز که دقیقاً این ۴ بخش رو داشته باشه:

🟢 تحلیل فاندامنتال
📊 تحلیل تکنیکال (طلا، فارکس، بیت‌کوین، اتریوم، بورس ایران)
🧠 روانشناسی بازار
🛡 مدیریت ریسک و سرمایه

قوانین:
- لحن حرفه‌ای ولی خودمونی، با ایموجی مناسب
- هر بخش حداکثر ۴-۵ خط
- در انتها یک خط دیسکلیمر: «این محتوا صرفاً جنبه آموزشی دارد و توصیه سرمایه‌گذاری نیست.»
- فقط خروجی نهایی رو بده، بدون توضیح اضافه"""


def generate_content(raw_news: str) -> str:
    now_tehran = datetime.now(TEHRAN_TZ)
    try:
        today_fa = jdatetime.datetime.fromgregorian(datetime=now_tehran).strftime("%Y/%m/%d")
    except Exception:
        today_fa = now_tehran.strftime("%Y-%m-%d")

    user_prompt = (
        f"تاریخ شمسی امروز: {today_fa}\n\n"
        f"خبرهای خام امروز:\n{raw_news or '(فیدها خبر جدیدی نداشتند، بر اساس روند کلی بازار بنویس)'}"
    )
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    last_err = None
    for attempt in range(3):
        try:
            resp = requests.post(
                MISTRAL_URL,
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            if resp.status_code == 429:
                wait = 10 * (attempt + 1)
                logger.warning(f"Mistral rate limit, sleep {wait}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            logger.warning(f"Mistral attempt {attempt+1} failed: {e}")
            time.sleep(3)
    raise RuntimeError(f"Mistral API failed after 3 attempts: {last_err}")


# ---------- ارسال پیش‌نویس برای تأیید ----------
async def send_draft_for_approval():
    logger.info("در حال تهیه محتوای روزانه...")
    try:
        raw_news = fetch_news()
        content = generate_content(raw_news)
    except Exception as e:
        logger.exception("خطا در تولید محتوا")
        try:
            await bot.send_message(ADMIN_CHAT_ID, f"⚠️ خطا در تولید محتوا: {e}")
        except Exception:
            pass
        return

    # محدودیت ۴۰۹۶ کاراکتر تلگرام
    if len(content) > 3800:
        content = content[:3800] + "\n\n...(ادامه)"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ تایید و انتشار", callback_data="approve"),
        InlineKeyboardButton("❌ رد", callback_data="reject"),
    ]])
    await bot.send_message(
        ADMIN_CHAT_ID,
        DRAFT_PREFIX + content,
        reply_markup=keyboard,
    )


async def handle_update(update: Update):
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        if q.from_user.id != ADMIN_CHAT_ID:
            logger.warning(f"Unauthorized callback from {q.from_user.id}")
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


# ---------- مسیرهای وب ----------
@flask_app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        asyncio.run(handle_update(update))
    except Exception as e:
        logger.exception(f"webhook error: {e}")
    return "ok"


@flask_app.route(f"/trigger-daily/{WEBHOOK_SECRET}", methods=["GET"])
def trigger_daily():
    try:
        asyncio.run(send_draft_for_approval())
        return "triggered"
    except Exception as e:
        logger.exception(f"trigger-daily error: {e}")
        return "error", 500


@flask_app.route("/")
def health():
    return "Metatya Bot is alive ✅"


# ---------- ثبت خودکار وب‌هوک ----------
def _set_webhook():
    time.sleep(5)  # صبر تا سرور کامل بالا بیاد
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        hook_url = f"{PUBLIC_URL.rstrip('/')}/webhook/{WEBHOOK_SECRET}"
        resp = requests.post(url, json={"url": hook_url}, timeout=30)
        logger.info(f"Webhook set: {resp.json()}")
    except Exception as e:
        logger.error(f"setWebhook failed: {e}")


# ---------- اجرای اصلی ----------
if __name__ == "__main__":
    threading.Thread(target=_set_webhook, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
