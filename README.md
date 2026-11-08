# Metatya — راهنمای ساخت پروژه از صفر تا صد

این راهنما جایگزین README قدیمی است. README قبلی درباره‌ی Gemini، Mistral و Cloudflare برای تولید محتوا و متغیر `POLISH` بود. کد فعلی برای تولید محتوا فقط از **OpenRouter** استفاده می‌کند و متغیر `POLISH` دیگر وجود ندارد.

ترتیب بخش‌ها را دقیق دنبال کن. هر بخش به بخش قبلی وابسته است.

---

## ۰. نقشه‌ی پروژه

| بخش | چه کاری می‌کند |
|---|---|
| `.github/workflows/daily.yml` | هر روز ساعت ۸ صبح (به وقت تهران) محتوا می‌سازد، سایت را به‌روز می‌کند و پست منتشر می‌کند |
| `.github/workflows/deploy-bots.yml` | Worker ربات‌های فروش را در Cloudflare منتشر و webhook هر ربات را ثبت می‌کند |
| `.github/workflows/health.yml` | هر ۶ ساعت سلامت سایت و تازگی محتوا را بررسی می‌کند |
| `scripts/` | کدهای پایتون: جمع‌آوری داده، تولید محتوا، ساخت صفحات، ویدیو، ارسال تلگرام، جستجوی فرصت |
| `worker/` | کد Cloudflare Worker ربات‌های فروش (`index.js`) و تنظیمات آن (`wrangler.toml`) |
| `docs/` | خود سایت (GitHub Pages). هر چیزی در این پوشه عمومی منتشر می‌شود |
| `docs/strategy/metatya-bot-charter-social-roadmap.md` | شرح وظایف ربات‌ها، وضعیت واقعی قابلیت‌ها و نقشه راه تلگرام، اینستاگرام و یوتیوب |
| `docs/index.html` | صفحه‌ی اصلی |
| `docs/home-2026.html` | نسخه‌ی قبلی صفحه‌ی اصلی (پشتیبان) |
| `docs/topic.html` | صفحه‌ی هر حوزه. اطلاعاتش را از `topics.json` و `content.json` می‌خواند |
| `docs/topics.json` | حوزه‌ها، آینده‌پژوهی، پیشنهادهای فروش، قیمت‌ها و یوزرنیم ربات‌ها |
| `docs/packs.json` | پک‌های فروش، قیمت‌ها و یوزرنیم ربات هر پک |
| `docs/services.html`، `docs/pack.html` | صفحه‌های سفارش خدمات |
| `docs/sport.html`، `docs/sport-elite-mind.html` | بخش ورزش و ویزیت ذهن ورزشی |
| `docs/cta.js` | فرم خبرنامه (Supabase) و دکمه‌های اشتراک‌گذاری |
| `docs/monetization.json` | پیشنهادهای درآمدی (لینک معرفی، محصولات) |
| `config/radar.json`، `data/` | تنظیمات و حافظه‌ی جستجوگر فرصت |
| `worker/wrangler.toml` | نام Worker و `SITE_URL` |

**پوشه‌های تولیدشده:** این‌ها هر روز خودکار ساخته می‌شوند. دستی ویرایششان نکن: `docs/content.json`، `docs/p/`، `docs/data/`، `docs/posted.json`، `docs/sitemap.xml`، `docs/feed.xml`، `docs/latest.json`.

---

## ۱. حساب‌ها و ابزارهایی که لازم داری

| سرویس | آدرس | برای چه | هزینه |
|---|---|---|---|
| GitHub | github.com | کد، سایت، اجرای خودکار | رایگان |
| OpenRouter | openrouter.ai | کلید مدل رایگان برای تولید محتوای روزانه | رایگان (سهمیه‌ی روزانه‌ی مدل‌های رایگان محدود است) |
| Telegram | telegram.org | کانال، ربات کانال، چت بازبینی، پنج ربات فروش | رایگان |
| Cloudflare | cloudflare.com | Worker ربات‌های فروش | رایگان |
| Supabase | supabase.com | ذخیره‌ی ایمیل خبرنامه | رایگان |
| کامپیوتر با Git یا GitHub Desktop | — | آپلود کل پروژه (توصیه‌شده) | — |

---

## ۲. ساخت ریپو و آپلود پروژه

### الف) ریپوی جدید
1. در GitHub روی **New repository** بزن. نام مثلاً `metatya` و نوع **Public** را انتخاب کن. گزینه‌های README و `.gitignore` را خالی بگذار و **Create repository** بزن.
2. فایل zip را از حالت فشرده خارج کن و پوشه‌ی `metatya` را ببین.
3. روی کامپیوتر، داخل پوشه‌ی `metatya` این دستورها را اجرا کن:

```bash
git init -b main
git add .
git commit -m "Initial Metatya project"
git remote add origin https://github.com/<نام‌کاربری>/metatya.git
git push -u origin main
```

4. **نکته:** پوشه‌ی `.github` مخفی است. آپلود از مرورگر معمولاً آن را جا می‌گذارد. پس از Git یا GitHub Desktop استفاده کن.

### ب) ریپوی موجود
فقط فایل‌هایی را که عوض شده‌اند جایگزین کن و commit بزن. فهرست کامل فایل‌ها در بخش ۰ است.

---

## ۳. فعال‌سازی سایت (GitHub Pages)

1. **Settings → Pages** را باز کن.
2. در بخش **Source** گزینه‌ی **Deploy from a branch** را انتخاب کن.
3. **Branch** را `main` و پوشه را `/docs` بگذار. **Save** بزن.
4. چند دقیقه صبر کن. آدرس سایت این می‌شود:
   `https://<نام‌کاربری>.github.io/<نام‌ریپو>/`
5. این آدرس را در بخش ۹ به‌عنوان Variable با نام `SITE_URL` وارد کن.

اگر آدرس اصلی سایت 404 داد، یعنی فایل `docs/index.html` در ریپو نیست.

---

## ۴. Supabase (خبرنامه و فایل‌های خصوصی)

پروژه‌ی فعال Metatya از قبل ساخته شده است. آدرس پروژه و کلید عمومی `anon` در `docs/site-config.js` قرار دارند. کلید عمومی برای مرورگر است؛ کلید محرمانه‌ی `service_role` هرگز نباید در سایت یا فایل‌های داخل `docs/` قرار بگیرد.

برای نصب تازه، جدول خبرنامه را با ساختار سازگار با فرم فعلی بساز:

```sql
create table if not exists public.leads (
  id uuid primary key default gen_random_uuid(),
  email text not null check (
    email ~* '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+

---

## ۵. OpenRouter (تولید محتوا)

1. در openrouter.ai وارد شو و از بخش **Keys** یک کلید بساز. کلید با `sk-or-` شروع می‌شود.
2. آن را در GitHub به‌عنوان Secret با نام `OPENROUTER_API_KEY` ذخیره کن.

برای تولید محتوا، `GEMINI_API_KEY`، `MISTRAL_API_KEY` و `CLOUDFLARE_API_TOKEN` لازم نیستند. اگر این‌ها را در GitHub داری، می‌توانی حذفشان کنی.

---

## ۶. تلگرام: کانال، ربات کانال و چت بازبینی

1. یک کانال بساز و یوزرنیم عمومی بگذار، مثلاً `@yourchannel`.
2. در @BotFather دستور `/newbot` را بزن و یک ربات برای کانال بساز. توکنش را نگه دار.
3. ربات را به کانال **ادمین** کن و اجازه‌ی **Post messages** بده.
4. توکن ربات را به‌صورت Secret و شناسه‌ی کانال را به‌صورت Variable ذخیره کن:
   - `TELEGRAM_BOT_TOKEN` = توکن ربات کانال
   - Variable `TELEGRAM_CHAT_ID` = `@Maytyafx` (یا یوزرنیم کانال خودت)
5. آیدی عددی خودت را از @userinfobot بگیر و به‌عنوان Secret با نام `TELEGRAM_REVIEW_CHAT_ID` ذخیره کن.
6. **مهم:** ربات کانال را در تلگرام باز کن و `/start` بزن. بدون این کار، ربات نمی‌تواند پیش‌نویس‌ها را برایت بفرستد.

---

## ۷. پنج ربات فروش

1. در @BotFather پنج ربات بساز: `risk`، `bourse`، `fit`، `mind`، `biz`. یوزرنیم هر کدام باید یکتا باشد و به `bot` ختم شود، مثلاً `yourbrand_risk_bot`.
2. توکن هر ربات را به Secret با این نام‌ها ببر:
   `BOT_RISK`، `BOT_BOURSE`، `BOT_FIT`، `BOT_MIND`، `BOT_BIZ`
3. یوزرنیم هر ربات (بدون @) را در این فایل‌ها بگذار:
   - `docs/topics.json`: بخش `bots` (پنج کلید)
   - `docs/packs.json`: فیلد `bot` در هر پنج پک
   - `docs/services.html`: `var ORDER_BOT="..."` (بات risk)
   - `docs/sport-elite-mind.html`: `const ORDER_BOT = '...'` (بات mind)
4. توکن‌ها هرگز داخل فایل‌ها نروند. فقط در Secrets.

---

## ۸. Cloudflare Worker

Worker فعلی پنج مسیر ربات تلگرام دارد: `/tg/risk`، `/tg/bourse`، `/tg/fit`، `/tg/mind` و `/tg/biz`. استقرار موفق آن در GitHub Actions ثبت شده است.

برای استقرار مجدد:
1. در Cloudflare یک `workers.dev` subdomain فعال داشته باش.
2. یک API Token با دسترسی محدود **Edit Cloudflare Workers** بساز و آن را در GitHub Secret با نام `CLOUDFLARE_DEPLOY_TOKEN` قرار بده.
3. شناسه حساب را در Secret با نام `CLOUDFLARE_ACCOUNT_ID` قرار بده.
4. مقدار `SITE_URL` را در تنظیمات Worker با آدرس GitHub Pages هماهنگ کن.
5. Secretهای ربات و webhook را فقط در GitHub Actions و Cloudflare Secrets نگه دار؛ هیچ توکنی نباید در کد عمومی باشد.

Worker برای تحویل فایل‌های خصوصی از bucket خصوصی Supabase استفاده می‌کند. تأیید پرداخت و ارسال نهایی در جریان فعلی دستی و با بازبینی مسئول انجام می‌شود؛ این فرایند درگاه پرداخت خودکار نیست.

---

## ۹. Secrets و Variables

مسیر: **Settings → Secrets and variables → Actions**. تب **Secrets** برای رمزها و تب **Variables** برای مقادیر غیرمحرمانه است.

### Secrets

| نام | از کجا | برای چه | ضروری؟ |
|---|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter | تولید محتوا | بله |
| `TELEGRAM_BOT_TOKEN` | BotFather (ربات کانال) | ارسال پست به کانال | بله |

| `TELEGRAM_REVIEW_CHAT_ID` | @userinfobot | پیش‌نویس و بازبینی سفارش‌ها | بله |
| `BOT_RISK`، `BOT_BOURSE`، `BOT_FIT`، `BOT_MIND`، `BOT_BIZ` | BotFather | توکن پنج ربات فروش | برای فروش بله |
| `WEBHOOK_SECRET` | خودت (رشته‌ی تصادفی بلند) | امنیت webhook | برای فروش بله |
| `PAY_INFO` | خودت | متن پرداخت (شماره کارت و نام صاحب حساب) | برای فروش بله |
| `CLOUDFLARE_DEPLOY_TOKEN` | Cloudflare | دیپلوی Worker | برای فروش بله |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare | شناسه‌ی حساب | برای فروش بله |
| `SUPABASE_SERVICE_KEY` | Supabase → Settings → API (service_role) | دسترسی سروری به فایل‌های خصوصی PRO در Worker و بارگذاری محصولات | برای تحویل فایل خصوصی لازم |

### Variables

| نام | مقدار | توضیح |
|---|---|---|
| `SITE_URL` | `https://<نام‌کاربری>.github.io/<نام‌ریپو>/` | آدرس سایت. پست‌ها و health check از آن استفاده می‌کنند |
| `TELEGRAM_CHAT_ID` | `@Maytyafx` | مقصد انتشار؛ در صورت خالی بودن همین کانال پیش‌فرض است |
| `POST_MODE` | `auto` (پیش‌فرض) یا `review` | `review` پیش‌نویس را فقط برای بازبینی می‌فرستد؛ `auto` مستقیم در کانال منتشر می‌کند |
| `POST_KEYS` | `forex,crypto,bourse` (اختیاری) | کدام حوزه‌ها پست شوند |
| `SUPABASE_URL` | `https://<project>.supabase.co` | اتصال سروری به Storage خصوصی و جمع‌آوری داده؛ کلید سرویس جداگانه و محرمانه است |

**نکته:** `SUPABASE_SERVICE_KEY` را هرگز در کد یا سایت نگذار.

---

## ۱۰. شخصی‌سازی (اگر برند دیگری می‌سازی)

این فایل‌ها هنوز نام و لینک برند فعلی را دارند. قبل از انتشار عوضشان کن:

- **لینک تلگرام** `https://t.me/maytya`: در `docs/topics.json` (فیلد `contact`)، `docs/packs.json` (فیلد `contact`) و `docs/cta.js` (آرایه‌ی `links`).
- **لینک یوتیوب و اینستاگرام:** در `docs/cta.js`.
- **نام برند و متن صفحات:** با جستجوی `maytya` و `متیا` در ریپو پیدا کن.
- **قیمت‌ها:** `docs/packs.json` (فیلد `price` و بخش `prices`)، `docs/topics.json` (فیلد `price` در هر پیشنهاد) و `docs/services.html` (بخش `CONFIG`).
- **شماره‌ی بحران ۱۱۵:** در `worker/index.js` (دو جا) و `docs/topics.json` (فیلد `disclaimer`). حتماً از منبع رسمی تأیید کن. ۱۱۵ در ایران معمولاً شماره‌ی اورژانس پزشکی است، نه خط مشاوره‌ی روانی.
- **پیشنهادهای درآمدی:** `docs/monetization.json` (بخش ۱۴).

---

## ۱۱. اولین اجرا (ترتیب دقیق)

1. **سایت:** آدرس GitHub Pages را باز کن. باید صفحه‌ی اصلی را ببینی.
2. **حالت انتشار:** مقدار پیش‌فرض `POST_MODE` برابر `auto` است. برای توقف انتشار مستقیم، در **Settings → Secrets and variables → Actions → Variables** مقدار `POST_MODE=review` بگذار؛ برای انتشار مستقیم، آن را روی `auto` قرار بده. مقصد پیش‌فرض کانال `@Maytyafx` است و با متغیر `TELEGRAM_CHAT_ID` قابل تغییر است.
3. **تولید روزانه:** Actions → **Metatya daily** → **Run workflow**. معمولاً چند دقیقه طول می‌کشد. اگر سبز شد، `docs/content.json` به‌روز شده است. اگر قرمز شد، لاگ را باز کن.
4. **بازبینی:** چت بازبینی تلگرامت را نگاه کن. پیش‌نویس پست‌ها باید آنجا باشد.
5. **دیپلوی Worker:** Actions → **Deploy sales bots (Cloudflare Worker, free)**. در اجرای موفق، بررسی اعتبار Cloudflare، استقرار Worker، بارگذاری Secretها و ثبت webhookها باید همگی موفق باشند.
6. **/start:** در هر پنج ربات فروش `/start` بزن.
7. **Health check:** Actions → **Metatya health check** → **Run workflow**. باید سبز شود.
8. **وقتی مطمئن شدی:** `POST_MODE` را `auto` کن.

---

## ۱۲. تست سفارش (از یک اکانت دوم)

1. صفحه‌ی یک حوزه را باز کن (مثلاً `topic.html?t=crypto`) و روی دکمه‌ی سفارش بزن. ربات باید باز شود.
2. فرم را پر کن. متن پرداخت باید با قیمت درست و `PAY_INFO` بیاید.
3. یک رسید یا پیام تست بفرست. تو باید آن را همراه دکمه‌ها دریافت کنی.
4. دکمه‌ی **واریز شد** را بزن. پیش‌نویس ساخته می‌شود.
5. پیش‌نویس را بازبینی کن و سپس ارسال کن.

---

## ۱۳. کار روزانه

- هر روز صبح پیش‌نویس پست‌ها را در چت بازبینی بخوان.
- سفارش‌ها: رسید را تأیید کن (دکمه‌ی «واریز شد»)، پیش‌نویس را بازبینی کن و بعد ارسال کن.
- health check هر ۶ ساعت اجرا می‌شود. اگر قرمز شد، گیت‌هاب برایت ایمیل می‌فرستد.

---

## ۱۴. درآمد و مبدأ ورود

- **پیشنهادهای درآمدی:** `docs/monetization.json` را ویرایش کن. متن‌های `_راهنما` و `_نمونه` را بخوان و آیتم واقعی خودت را داخل `items` بگذار. هر آیتم با برچسب «لینک معرفی» و `rel=sponsored` نمایش داده می‌شود.
- **قوانین:** قوانین تلگرام، یوتیوب، اینستاگرام و کشورت را درباره‌ی تبلیغ کارگزار و صرافی بررسی کن. هرگز سود تضمینی وعده نده.
- **مبدأ ورود:** لینک‌ها را با `?utm_source=youtube&utm_campaign=bourse` بساز. سایت مبدأ هر بازدیدکننده را کنار ایمیل خبرنامه ذخیره می‌کند.
- **گوگل:** بعد از زنده شدن سایت، `docs/sitemap.xml` را در Google Search Console ثبت کن.
- **موبایل:** سایت را در Chrome یا Safari باز کن و **Add to Home Screen** را بزن.

---

## ۱۵. خطاهای رایج و راه‌حل

| خطا یا علامت | علت | راه‌حل |
|---|---|---|
| آدرس اصلی سایت 404 | `docs/index.html` نیست | فایل `index.html` را در پوشه‌ی `docs` بگذار |
| health: `SITE_URL تنظیم نشده` | Variable نیست | بخش ۹ را ببین |
| Deploy: `No access to the specified resource` | توکن یا Account ID اشتباه است | توکن جدید با قالب Edit Cloudflare Workers و Account ID درست بساز |
| Deploy: `workers.dev subdomain` | subdomain ثبت نشده | بخش ۸، مرحله ۱ |
| Deploy: `exit code 1` بدون جزئیات | جزئیات در بخش جمع‌شده‌ی لاگ است | مثلث کنار «Running Wrangler Commands» را باز کن |
| بات جواب نمی‌دهد | `/start` نزده‌ای یا یوزرنیم اشتباه است | `/start` بزن و لینک `t.me/...` را بررسی کن |
| پست به کانال نمی‌رود | ربات ادمین کانال نیست | ربات را ادمین کن و اجازه‌ی ارسال بده |
| پیش‌نویس به تلگرام نمی‌آید | `/start` را در ربات کانال نزده‌ای | `/start` بزن |
| daily: `OPENROUTER_API_KEY تنظیم نشده` | Secret نیست | بخش ۵ |
| `business` یا `law` در health «خراب» است | کیفیت محتوای آن روز کم بوده | عادی است. بعداً بررسی کن |
| هشدار Node.js 20 یا ubuntu-latest | هشدار GitHub | فعلاً نادیده بگیر |
| تلگرام باز نمی‌شود | فیلتر تلگرام در ایران | از VPN استفاده کن |
| پست تکراری منتشر شده | `posted.json` جلوی آن را می‌گیرد | برای ارسال عمدی مجدد، متغیر `FORCE_POST=1` را بگذار |

---

## ۱۶. قبل از فروش واقعی

- شماره‌ی ۱۱۵ را از منبع رسمی تأیید کن (بخش ۱۰).
- برای ویزیت ذهن ورزشی، مدرک یا پروانه‌ی مشاور را روشن کن.
- برای ارجاع حقوقی، فقط با وکیل پروانه‌دار و توافق مکتوب کار کن.
- برای خدمات مالی و بورس، بررسی کن که مجوز لازم داری یا نه.
- شرایط بازپرداخت را در `CONFIG.refund` (فایل `docs/services.html`) بنویس.
- متن هشدار (disclaimer) هر صفحه‌ی خدمت را بخوان.
- هیچ‌جا سود تضمینی، سیگنال خرید یا فروش، یا وعده‌ی نتیجه نده.

---

## ۱۷. امنیت

- توکن‌ها، رمزها و `PAY_INFO` هرگز داخل فایل‌های ریپو نباشند.
- اگر توکنی لو رفت، فوراً آن را در BotFather، Cloudflare یا OpenRouter باطل کن و یک توکن جدید بساز.
- `service_role` فقط داخل Secrets باشد.
- ربات‌های Node قدیمی (پوشه‌ی `metatya-bots`) را همزمان با این سیستم اجرا نکن تا پست تکراری نشود.

---

## ۱۸. تست محلی (اختیاری و بدون API)

دستور `python scripts/generate.py --dry` محتوای نمونه می‌سازد و `docs/content.json` را بازنویسی می‌کند. قبل از اجرا یک کپی از فایل بگیر.

## استاندارد طراحی رابط کاربری

برای هر تغییر در رابط وب، ابتدا `AGENTS.md` و سپس [استاندارد طراحی فرانت‌اند متاتیا](docs/design-system/metatya-frontend-standards.md) را بخوان. این سند، اصول طراحی متمایز، UX، دسترس‌پذیری، حرکت، انتخاب کامپوننت و قواعد استفاده از منابع وب و موبایل را مشخص می‌کند. سایت فعلی همچنان HTML/CSS/JavaScript استاتیک است؛ راهنماهای Android و SwiftUI فقط برای اپ‌های بومی آینده کاربرد دارند.


---

## ۱۹. نسخه پشتیبان و بازیابی مخزن (به‌روزرسانی ۲۰۲۶-۱۱-۰۸)

شاخه پشتیبان مستقل از وضعیت فعلی main ایجاد شده است:

- نام شاخه: backup/2026-11-08
- نشانی مخزن: https://github.com/maytyafx-debug/maytya/tree/backup/2026-11-08

برای دریافت شاخه‌ها و رفتن به نسخه پشتیبان:

~~~bash
git fetch origin
git checkout backup/2026-11-08
~~~

برای ساخت یک بسته مستقل شامل تاریخچه و شاخه‌های دریافت‌شده:

~~~bash
git clone https://github.com/maytyafx-debug/maytya.git
cd maytya
git bundle create ../maytya-all-refs.bundle --all
~~~

برای بازگردانی یک کپی از bundle:

~~~bash
git clone ../maytya-all-refs.bundle maytya-restored
~~~

نکته: این پشتیبان شامل کد و فایل‌های ثبت‌شده در Git است؛ Secrets مربوط به GitHub Actions، توکن‌های تلگرام، تنظیمات Cloudflare، داده‌های Supabase و تنظیمات خارج از مخزن داخل شاخه Git قرار نمی‌گیرند. از تنظیمات و داده‌های سرویس‌های بیرونی جداگانه و به‌صورت امن نسخه پشتیبان تهیه کن.

    and length(email) <= 254
  ),
  source text check (source is null or length(source) <= 60),
  consent boolean not null default false check (consent = true),
  created_at timestamptz not null default now()
);

alter table public.leads enable row level security;
grant insert on public.leads to anon;

create policy "anon can insert leads"
  on public.leads
  for insert to anon
  with check (consent = true);
```

- برای اتصال یک پروژه‌ی تازه، فقط **Project URL** و **anon/publishable key** را در `docs/site-config.js` قرار بده.
- دسترسی عمومی جدول خبرنامه فقط برای `INSERT` با رضایت صریح است؛ برای `SELECT` عمومی سیاست نساز.
- در پروژه‌ی فعال، bucket با نام `paid-packs` خصوصی است. فایل‌های PRO عمومی نیستند و Worker فقط با کلید سروری ذخیره‌شده در GitHub Actions به آن‌ها دسترسی دارد.
- متغیر `SUPABASE_URL` و Secret با نام `SUPABASE_SERVICE_KEY` برای بارگذاری/تحویل فایل خصوصی در فرایند سروری استفاده می‌شوند. کلید سرویس را در مرورگر، `site-config.js` یا هیچ فایل عمومی قرار نده.
- `site-data.js` ابتدا جدول `site_content` را امتحان می‌کند و در صورت نبودن یا در دسترس نبودن آن، به فایل‌های JSON داخل مخزن برمی‌گردد. منبع قابل اتکای فعلی محتوا همان فایل‌های مخزن است.
- پیش از ساخت پروژه‌ی تازه، تنظیمات و سیاست‌های RLS را با وضعیت واقعی سرویس تطبیق بده؛ این دستورها برای نصب تازه‌اند و نباید کورکورانه روی دیتابیس فعال اجرا شوند.

---

## ۵. OpenRouter (تولید محتوا)

1. در openrouter.ai وارد شو و از بخش **Keys** یک کلید بساز. کلید با `sk-or-` شروع می‌شود.
2. آن را در GitHub به‌عنوان Secret با نام `OPENROUTER_API_KEY` ذخیره کن.

برای تولید محتوا، `GEMINI_API_KEY`، `MISTRAL_API_KEY` و `CLOUDFLARE_API_TOKEN` لازم نیستند. اگر این‌ها را در GitHub داری، می‌توانی حذفشان کنی.

---

## ۶. تلگرام: کانال، ربات کانال و چت بازبینی

1. یک کانال بساز و یوزرنیم عمومی بگذار، مثلاً `@yourchannel`.
2. در @BotFather دستور `/newbot` را بزن و یک ربات برای کانال بساز. توکنش را نگه دار.
3. ربات را به کانال **ادمین** کن و اجازه‌ی **Post messages** بده.
4. توکن ربات را به‌صورت Secret و شناسه‌ی کانال را به‌صورت Variable ذخیره کن:
   - `TELEGRAM_BOT_TOKEN` = توکن ربات کانال
   - Variable `TELEGRAM_CHAT_ID` = `@Maytyafx` (یا یوزرنیم کانال خودت)
5. آیدی عددی خودت را از @userinfobot بگیر و به‌عنوان Secret با نام `TELEGRAM_REVIEW_CHAT_ID` ذخیره کن.
6. **مهم:** ربات کانال را در تلگرام باز کن و `/start` بزن. بدون این کار، ربات نمی‌تواند پیش‌نویس‌ها را برایت بفرستد.

---

## ۷. پنج ربات فروش

1. در @BotFather پنج ربات بساز: `risk`، `bourse`، `fit`، `mind`، `biz`. یوزرنیم هر کدام باید یکتا باشد و به `bot` ختم شود، مثلاً `yourbrand_risk_bot`.
2. توکن هر ربات را به Secret با این نام‌ها ببر:
   `BOT_RISK`، `BOT_BOURSE`، `BOT_FIT`، `BOT_MIND`، `BOT_BIZ`
3. یوزرنیم هر ربات (بدون @) را در این فایل‌ها بگذار:
   - `docs/topics.json`: بخش `bots` (پنج کلید)
   - `docs/packs.json`: فیلد `bot` در هر پنج پک
   - `docs/services.html`: `var ORDER_BOT="..."` (بات risk)
   - `docs/sport-elite-mind.html`: `const ORDER_BOT = '...'` (بات mind)
4. توکن‌ها هرگز داخل فایل‌ها نروند. فقط در Secrets.

---

## ۸. Cloudflare (Worker ربات‌های فروش)

1. در dash.cloudflare.com وارد شو. یک بار **workers.dev subdomain** را از بخش Workers & Pages ثبت کن.
2. **My Profile → API Tokens → Create Token** را بزن. قالب **Edit Cloudflare Workers** را انتخاب کن، حساب خودت را در بخش Account Resources بگذار و **Create** بزن. توکن را کپی کن. فقط یک بار نشان داده می‌شود.
3. توکن را به Secret با نام `CLOUDFLARE_DEPLOY_TOKEN` ببر.
4. **Account ID** را از صفحه‌ی اصلی داشبورد کپی کن و به Secret با نام `CLOUDFLARE_ACCOUNT_ID` ببر.
5. در فایل `worker/wrangler.toml` مقدار `SITE_URL` را به آدرس سایت خودت (بخش ۳) عوض کن.

---

## ۹. Secrets و Variables

مسیر: **Settings → Secrets and variables → Actions**. تب **Secrets** برای رمزها و تب **Variables** برای مقادیر غیرمحرمانه است.

### Secrets

| نام | از کجا | برای چه | ضروری؟ |
|---|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter | تولید محتوا | بله |
| `TELEGRAM_BOT_TOKEN` | BotFather (ربات کانال) | ارسال پست به کانال | بله |

| `TELEGRAM_REVIEW_CHAT_ID` | @userinfobot | پیش‌نویس و بازبینی سفارش‌ها | بله |
| `BOT_RISK`، `BOT_BOURSE`، `BOT_FIT`، `BOT_MIND`، `BOT_BIZ` | BotFather | توکن پنج ربات فروش | برای فروش بله |
| `WEBHOOK_SECRET` | خودت (رشته‌ی تصادفی بلند) | امنیت webhook | برای فروش بله |
| `PAY_INFO` | خودت | متن پرداخت (شماره کارت و نام صاحب حساب) | برای فروش بله |
| `CLOUDFLARE_DEPLOY_TOKEN` | Cloudflare | دیپلوی Worker | برای فروش بله |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare | شناسه‌ی حساب | برای فروش بله |
| `SUPABASE_SERVICE_KEY` | Supabase → Settings → API (service_role) | جدول `data_bank` | اختیاری |

### Variables

| نام | مقدار | توضیح |
|---|---|---|
| `SITE_URL` | `https://<نام‌کاربری>.github.io/<نام‌ریپو>/` | آدرس سایت. پست‌ها و health check از آن استفاده می‌کنند |
| `TELEGRAM_CHAT_ID` | `@Maytyafx` | مقصد انتشار؛ در صورت خالی بودن همین کانال پیش‌فرض است |
| `POST_MODE` | `auto` (پیش‌فرض) یا `review` | `review` پیش‌نویس را فقط برای بازبینی می‌فرستد؛ `auto` مستقیم در کانال منتشر می‌کند |
| `POST_KEYS` | `forex,crypto,bourse` (اختیاری) | کدام حوزه‌ها پست شوند |
| `SUPABASE_URL` | `https://<project>.supabase.co` | فقط اگر `data_bank` را فعال می‌کنی |

**نکته:** `SUPABASE_SERVICE_KEY` را هرگز در کد یا سایت نگذار.

---

## ۱۰. شخصی‌سازی (اگر برند دیگری می‌سازی)

این فایل‌ها هنوز نام و لینک برند فعلی را دارند. قبل از انتشار عوضشان کن:

- **لینک تلگرام** `https://t.me/maytya`: در `docs/topics.json` (فیلد `contact`)، `docs/packs.json` (فیلد `contact`) و `docs/cta.js` (آرایه‌ی `links`).
- **لینک یوتیوب و اینستاگرام:** در `docs/cta.js`.
- **نام برند و متن صفحات:** با جستجوی `maytya` و `متیا` در ریپو پیدا کن.
- **قیمت‌ها:** `docs/packs.json` (فیلد `price` و بخش `prices`)، `docs/topics.json` (فیلد `price` در هر پیشنهاد) و `docs/services.html` (بخش `CONFIG`).
- **شماره‌ی بحران ۱۱۵:** در `worker/index.js` (دو جا) و `docs/topics.json` (فیلد `disclaimer`). حتماً از منبع رسمی تأیید کن. ۱۱۵ در ایران معمولاً شماره‌ی اورژانس پزشکی است، نه خط مشاوره‌ی روانی.
- **پیشنهادهای درآمدی:** `docs/monetization.json` (بخش ۱۴).

---

## ۱۱. اولین اجرا (ترتیب دقیق)

1. **سایت:** آدرس GitHub Pages را باز کن. باید صفحه‌ی اصلی را ببینی.
2. **Variables:** `POST_MODE` را `review` بگذار.
3. **تولید روزانه:** Actions → **Metatya daily** → **Run workflow**. معمولاً چند دقیقه طول می‌کشد. اگر سبز شد، `docs/content.json` به‌روز شده است. اگر قرمز شد، لاگ را باز کن.
4. **بازبینی:** چت بازبینی تلگرامت را نگاه کن. پیش‌نویس پست‌ها باید آنجا باشد.
5. **دیپلوی ربات‌ها:** Actions → **Deploy sales bots (Cloudflare Worker, free)** → **Run workflow**. در لاگ باید خط `secrets:` هشت کلید را نشان دهد: پنج `BOT_*`، `WEBHOOK_SECRET`، `OWNER_CHAT_ID` و `PAY_INFO`.
6. **/start:** در هر پنج ربات فروش `/start` بزن.
7. **Health check:** Actions → **Metatya health check** → **Run workflow**. باید سبز شود.
8. **وقتی مطمئن شدی:** `POST_MODE` را `auto` کن.

---

## ۱۲. تست سفارش (از یک اکانت دوم)

1. صفحه‌ی یک حوزه را باز کن (مثلاً `topic.html?t=crypto`) و روی دکمه‌ی سفارش بزن. ربات باید باز شود.
2. فرم را پر کن. متن پرداخت باید با قیمت درست و `PAY_INFO` بیاید.
3. یک رسید یا پیام تست بفرست. تو باید آن را همراه دکمه‌ها دریافت کنی.
4. دکمه‌ی **واریز شد** را بزن. پیش‌نویس ساخته می‌شود.
5. پیش‌نویس را بازبینی کن و سپس ارسال کن.

---

## ۱۳. کار روزانه

- هر روز صبح پیش‌نویس پست‌ها را در چت بازبینی بخوان.
- سفارش‌ها: رسید را تأیید کن (دکمه‌ی «واریز شد»)، پیش‌نویس را بازبینی کن و بعد ارسال کن.
- health check هر ۶ ساعت اجرا می‌شود. اگر قرمز شد، گیت‌هاب برایت ایمیل می‌فرستد.

---

## ۱۴. درآمد و مبدأ ورود

- **پیشنهادهای درآمدی:** `docs/monetization.json` را ویرایش کن. متن‌های `_راهنما` و `_نمونه` را بخوان و آیتم واقعی خودت را داخل `items` بگذار. هر آیتم با برچسب «لینک معرفی» و `rel=sponsored` نمایش داده می‌شود.
- **قوانین:** قوانین تلگرام، یوتیوب، اینستاگرام و کشورت را درباره‌ی تبلیغ کارگزار و صرافی بررسی کن. هرگز سود تضمینی وعده نده.
- **مبدأ ورود:** لینک‌ها را با `?utm_source=youtube&utm_campaign=bourse` بساز. سایت مبدأ هر بازدیدکننده را کنار ایمیل خبرنامه ذخیره می‌کند.
- **گوگل:** بعد از زنده شدن سایت، `docs/sitemap.xml` را در Google Search Console ثبت کن.
- **موبایل:** سایت را در Chrome یا Safari باز کن و **Add to Home Screen** را بزن.

---

## ۱۵. خطاهای رایج و راه‌حل

| خطا یا علامت | علت | راه‌حل |
|---|---|---|
| آدرس اصلی سایت 404 | `docs/index.html` نیست | فایل `index.html` را در پوشه‌ی `docs` بگذار |
| health: `SITE_URL تنظیم نشده` | Variable نیست | بخش ۹ را ببین |
| Deploy: `No access to the specified resource` | توکن یا Account ID اشتباه است | توکن جدید با قالب Edit Cloudflare Workers و Account ID درست بساز |
| Deploy: `workers.dev subdomain` | subdomain ثبت نشده | بخش ۸، مرحله ۱ |
| Deploy: `exit code 1` بدون جزئیات | جزئیات در بخش جمع‌شده‌ی لاگ است | مثلث کنار «Running Wrangler Commands» را باز کن |
| بات جواب نمی‌دهد | `/start` نزده‌ای یا یوزرنیم اشتباه است | `/start` بزن و لینک `t.me/...` را بررسی کن |
| پست به کانال نمی‌رود | ربات ادمین کانال نیست | ربات را ادمین کن و اجازه‌ی ارسال بده |
| پیش‌نویس به تلگرام نمی‌آید | `/start` را در ربات کانال نزده‌ای | `/start` بزن |
| daily: `OPENROUTER_API_KEY تنظیم نشده` | Secret نیست | بخش ۵ |
| `business` یا `law` در health «خراب» است | کیفیت محتوای آن روز کم بوده | عادی است. بعداً بررسی کن |
| هشدار Node.js 20 یا ubuntu-latest | هشدار GitHub | فعلاً نادیده بگیر |
| تلگرام باز نمی‌شود | فیلتر تلگرام در ایران | از VPN استفاده کن |
| پست تکراری منتشر شده | `posted.json` جلوی آن را می‌گیرد | برای ارسال عمدی مجدد، متغیر `FORCE_POST=1` را بگذار |

---

## ۱۶. قبل از فروش واقعی

- شماره‌ی ۱۱۵ را از منبع رسمی تأیید کن (بخش ۱۰).
- برای ویزیت ذهن ورزشی، مدرک یا پروانه‌ی مشاور را روشن کن.
- برای ارجاع حقوقی، فقط با وکیل پروانه‌دار و توافق مکتوب کار کن.
- برای خدمات مالی و بورس، بررسی کن که مجوز لازم داری یا نه.
- شرایط بازپرداخت را در `CONFIG.refund` (فایل `docs/services.html`) بنویس.
- متن هشدار (disclaimer) هر صفحه‌ی خدمت را بخوان.
- هیچ‌جا سود تضمینی، سیگنال خرید یا فروش، یا وعده‌ی نتیجه نده.

---

## ۱۷. امنیت

- توکن‌ها، رمزها و `PAY_INFO` هرگز داخل فایل‌های ریپو نباشند.
- اگر توکنی لو رفت، فوراً آن را در BotFather، Cloudflare یا OpenRouter باطل کن و یک توکن جدید بساز.
- `service_role` فقط داخل Secrets باشد.
- ربات‌های Node قدیمی (پوشه‌ی `metatya-bots`) را همزمان با این سیستم اجرا نکن تا پست تکراری نشود.

---

## ۱۸. تست محلی (اختیاری و بدون API)

دستور `python scripts/generate.py --dry` محتوای نمونه می‌سازد و `docs/content.json` را بازنویسی می‌کند. قبل از اجرا یک کپی از فایل بگیر.

## استاندارد طراحی رابط کاربری

برای هر تغییر در رابط وب، ابتدا `AGENTS.md` و سپس [استاندارد طراحی فرانت‌اند متاتیا](docs/design-system/metatya-frontend-standards.md) را بخوان. این سند، اصول طراحی متمایز، UX، دسترس‌پذیری، حرکت، انتخاب کامپوننت و قواعد استفاده از منابع وب و موبایل را مشخص می‌کند. سایت فعلی همچنان HTML/CSS/JavaScript استاتیک است؛ راهنماهای Android و SwiftUI فقط برای اپ‌های بومی آینده کاربرد دارند.


---

## ۱۹. نسخه پشتیبان و بازیابی مخزن (به‌روزرسانی ۲۰۲۶-۱۱-۰۸)

شاخه پشتیبان مستقل از وضعیت فعلی main ایجاد شده است:

- نام شاخه: backup/2026-11-08
- نشانی مخزن: https://github.com/maytyafx-debug/maytya/tree/backup/2026-11-08

برای دریافت شاخه‌ها و رفتن به نسخه پشتیبان:

~~~bash
git fetch origin
git checkout backup/2026-11-08
~~~

برای ساخت یک بسته مستقل شامل تاریخچه و شاخه‌های دریافت‌شده:

~~~bash
git clone https://github.com/maytyafx-debug/maytya.git
cd maytya
git bundle create ../maytya-all-refs.bundle --all
~~~

برای بازگردانی یک کپی از bundle:

~~~bash
git clone ../maytya-all-refs.bundle maytya-restored
~~~

نکته: این پشتیبان شامل کد و فایل‌های ثبت‌شده در Git است؛ Secrets مربوط به GitHub Actions، توکن‌های تلگرام، تنظیمات Cloudflare، داده‌های Supabase و تنظیمات خارج از مخزن داخل شاخه Git قرار نمی‌گیرند. از تنظیمات و داده‌های سرویس‌های بیرونی جداگانه و به‌صورت امن نسخه پشتیبان تهیه کن.
