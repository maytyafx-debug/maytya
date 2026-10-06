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

## راه‌اندازی درآمد (مهم‌ترین بخش)
1. فایل docs/monetization.json را در گیت‌هاب ویرایش کنید: آیتم‌های `_نمونه` را (با لینک و متن واقعی خودتان) به آرایه `items` ببرید. بدون هیچ کدنویسی، همان لحظه در همه‌ی صفحه‌ها نمایش داده می‌شود.
2. هر آیتم affiliate خودکار با برچسب «لینک معرفی» و rel=sponsored نمایش داده می‌شود. قوانین یوتیوب/اینستاگرام/تلگرام و قوانین کشور خودتان درباره تبلیغ بروکر و صرافی را بررسی کنید؛ هرگز سود تضمینی وعده ندهید.
3. ایمیل‌های خبرنامه در جدول `leads` سوپابیس ذخیره می‌شود (فقط با کلید مدیریتی قابل خواندن است).
4. هر روز برای هر مطلب یک صفحه‌ی مستقل SEO + sitemap.xml + feed.xml ساخته می‌شود. sitemap را در Google Search Console ثبت کنید (رایگان).
5. متن آماده‌ی عنوان و توضیح هر شورت در Artifacts > shorts (فایل *_upload.txt) است.

## نکات عیب‌یابی
- فونت ویدیو: ابتدا Vazirmatn دانلود می‌شود؛ اگر نشد از assets/fonts/DejaVuSans.ttf (همراه ریپو، مجوز آزاد DejaVu) استفاده می‌شود. شکل‌دهی فارسی با Pillow+RAQM انجام می‌شود (libraqm0 در ورک‌فلو نصب می‌شود).
- پست تکراری تلگرام: وضعیت ارسال در docs/posted.json ثبت می‌شود. برای ارسال مجدد عمدی متغیر FORCE_POST=1 بگذارید.
- ربات‌های Node قدیمی پوشه‌ی metatya-bots (مبتنی بر Anthropic پولی) را هم‌زمان با این سیستم اجرا نکنید تا پست تکراری نرود.
