# Metatya — اجرای خودکار روزانه (رایگان)
1. ریپازیتوری GitHub بسازید و همه‌ی این پوشه را (با پوشه مخفی .github) آپلود کنید.
2. Settings > Secrets and variables > Actions. **حداقل یکی** از این کلیدهای رایگان (ترتیب کیفیت؛ اگر چند تا بگذارید خودکار پشتیبان هم می‌شوند):
   - GEMINI_API_KEY (aistudio.google.com، بهترین فارسی)
   - CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID (Workers AI)
   - MISTRAL_API_KEY (console.mistral.ai)
   - برای تلگرام: TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID (مثلاً @maytya)
   - در Variables: SITE_URL = https://نام‌کاربری.github.io/نام‌ریپو/
3. Settings > Pages > Deploy from branch > main > پوشه /docs
4. Actions > Metatya daily > Run workflow (یک‌بار برای تست). از آن به بعد هر روز خودکار اجرا می‌شود.
5. Actions > Metatya health check هر ۶ ساعت سایت را چک می‌کند؛ اگر قطع یا بیش از ۳۶ ساعت کهنه باشد قرمز می‌شود و گیت‌هاب ایمیل می‌دهد.
- نصب روی گوشی: سایت را در Chrome/Safari باز کنید > Add to Home Screen (PWA).
- بک‌آپ: هر روز docs/content.json در تاریخچه git ذخیره می‌شود.
- ویدیوهای ۱۰ ثانیه‌ای: Actions > Artifacts > shorts (آپلود خودکار نیاز به تأیید API گوگل/متا دارد).
- تست محلی بدون API: python scripts/generate.py --dry  (فایل docs/content.json را با نمونه جایگزین می‌کند؛ قبلش کپی بگیرید)
