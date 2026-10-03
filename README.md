# Metatya — اجرای خودکار روزانه (رایگان)
1. یک ریپازیتوری GitHub بسازید و این پوشه را آپلود کنید.
2. Settings > Secrets > Actions: ANTHROPIC_API_KEY ، TELEGRAM_BOT_TOKEN (از @BotFather) ، TELEGRAM_CHAT_ID . در Variables: SITE_URL
3. Settings > Pages > Deploy from branch، پوشه /docs (سایت رایگان و ۲۴ ساعته)
4. Actions > Metatya daily > Run workflow برای تست. بعد از آن هر روز خودکار اجرا می‌شود.
- بک‌آپ: هر روز content.json در تاریخچه git ذخیره می‌شود.
- ویدیوهای ۱۰ ثانیه‌ای: از Actions > Artifacts > shorts دانلود و در Shorts/Reels/تلگرام آپلود کنید (آپلود خودکار نیاز به تأیید API گوگل/متا دارد).
- تست محلی بدون API: python scripts/generate.py --dry
