# اجرای روزانه‌ی Metatya با داکر

## ساخت ایمیج
    docker build -t metatya-daily .

## فایل تنظیمات (.env)
یک فایل `.env` کنار پروژه بساز؛ **هرگز این فایل را در گیت commit نکن**:

    OPENROUTER_API_KEY=...
    TELEGRAM_BOT_TOKEN=...
    TELEGRAM_CHAT_ID=...
    TELEGRAM_REVIEW_CHAT_ID=...
    POST_MODE=...
    POST_KEYS=...
    SITE_URL=https://maytyafx-debug.github.io/maytya
    SUPABASE_URL=https://megbqtoihsuouiaxpifl.supabase.co
    SUPABASE_SERVICE_KEY=...

مقدارها را از GitHub Settings → Secrets و Variables بردار (همان نام‌ها).

## اجرای دستی
    docker run --rm --env-file .env \
      -v "$PWD/docs:/app/docs" -v "$PWD/data:/app/data" \
      metatya-daily

خروجی صفحات در `docs/` و داده‌ها در `data/` روی سرور ذخیره می‌شوند.

## اجرای خودکار روزانه (cron، ساعت ۸ صبح تهران = ۴:۳۰ UTC)
    30 4 * * * cd /opt/metatya && docker run --rm --env-file .env -v /opt/metatya/docs:/app/docs -v /opt/metatya/data:/app/data metatya-daily >> /var/log/metatya.log 2>&1

## نکته‌ها
- مرحله‌ی commit و push به GitHub داخل ایمیج نیست. اگر می‌خواهی خروجی به سایت GitHub Pages برود، روی سرور `git add docs data && git commit && git push` را جداگانه اجرا کن (با کلید دسترسی جدا).
- ربات‌های فروش (worker) روی Cloudflare می‌مانند و با workflow «Deploy sales bots» دیپلوی می‌شوند؛ ربطی به این داکر ندارند.
- خروجی PDF خصوصی (`private_packs/`) فقط آپلود به Supabase می‌شود و روی سرور نگه داشته نمی‌شود.
