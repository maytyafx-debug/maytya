from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

CHANGES = []
ERRORS = []

def read(path):
    return path.read_text(encoding="utf-8")

def save(path, content):
    old = read(path) if path.exists() else None

    if old == content:
        return

    if old is not None:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            shutil.copy2(path, backup)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    CHANGES.append(str(path.relative_to(ROOT)))

def replace_once(text, old, new, label):
    count = text.count(old)

    if count == 0:
        if new in text:
            return text
        ERRORS.append("عبارت پیدا نشد: " + label)
        return text

    return text.replace(old, new)

def make_topic(
    slug, name, tab, scene, accent,
    category, tagline, lead, future, disclaimer
):
    return {
        "slug": slug,
        "name": name,
        "tab": tab,
        "scene": scene,
        "accent": accent,
        "category": category,
        "tagline": tagline,
        "lead": lead,
        "future": future,
        "offers": [],
        "disclaimer": disclaimer
    }


def fix_topics():
    path = DOCS / "topics.json"
    data = json.loads(read(path))

    data["contact"] = "https://t.me/Maytyafx"

    existing = {
        item.get("slug")
        for item in data.get("topics", [])
    }

    sport = make_topic(
        "sport",
        "ورزش و عملکرد",
        "sport",
        "orbs",
        "lime",
        "آموزش ورزشی",
        "پیشرفت ورزشی با یادگیری، ایمنی و استمرار.",
        (
            "این بخش به سواد ورزشی، اصول ایمنی، شناخت مهارت‌ها، "
            "بازیابی و آمادگی ذهنی می‌پردازد. برنامه فردی باید "
            "با شرایط شخص و راهنمایی مربی واجد صلاحیت متناسب باشد."
        ),
        [
            {
                "years": "۲۰۲۷–۲۰۲۸",
                "title": "ارزیابی مهارت به‌جای مقایسه",
                "why": "پیشرفت پایدار با سنجش روند شخصی و کیفیت مهارت بهتر دیده می‌شود.",
                "meaning": "روی یادگیری مهارت و بازخورد مربی تمرکز کن."
            },
            {
                "years": "۲۰۲۷–۲۰۳۰",
                "title": "ایمنی و بازیابی در کنار تمرین",
                "why": "استراحت، تجهیزات مناسب و پیشگیری از آسیب بخش مهم آموزش ورزشی‌اند.",
                "meaning": "نشانه‌های خستگی و ناراحتی را جدی بگیر و از مربی کمک بگیر."
            },
            {
                "years": "۲۰۲۸–۲۰۳۰",
                "title": "آمادگی ذهنی و مهارت رقابت",
                "why": "تمرکز، مدیریت فشار و برنامه‌ریزی در ورزش سازمان‌یافته اهمیت دارند.",
                "meaning": "مهارت‌های ذهنی را با بازخورد تخصصی همراه کن."
            }
        ],
        "محتوا آموزشی است و جایگزین ارزیابی پزشکی یا برنامه‌ریزی مربی واجد صلاحیت نیست."
    )

    health = make_topic(
        "health",
        "سلامت و سبک زندگی",
        "health",
        "orbs",
        "cool",
        "سواد سلامت",
        "عادت‌های کوچک، آگاهی بیشتر درباره سلامت.",
        (
            "این بخش برای افزایش آگاهی عمومی درباره خواب، استراحت، "
            "بهداشت روزمره و مراجعه به متخصص طراحی شده است؛ "
            "نه تشخیص بیماری یا تجویز درمان."
        ),
        [
            {
                "years": "۲۰۲۷–۲۰۲۸",
                "title": "سواد سلامت دیجیتال",
                "why": "دسترسی به اطلاعات سلامت بیشتر شده، اما کیفیت منابع یکسان نیست.",
                "meaning": "اطلاعات مهم را با منابع معتبر و متخصص بررسی کن."
            },
            {
                "years": "۲۰۲۷–۲۰۳۰",
                "title": "توجه به خواب و بازیابی",
                "why": "خواب و استراحت از موضوعات مهم سلامت عمومی‌اند.",
                "meaning": "برای نگرانی‌های پایدار خواب یا سلامت با متخصص مشورت کن."
            },
            {
                "years": "۲۰۲۸–۲۰۳۰",
                "title": "پیشگیری و پیگیری منظم",
                "why": "آگاهی از مراقبت‌های پیشگیرانه به تصمیم‌گیری آگاهانه کمک می‌کند.",
                "meaning": "توصیه‌های مناسب شرایطت را از متخصص سلامت بپرس."
            }
        ],
        "این محتوا آموزشی و عمومی است؛ تشخیص، درمان یا توصیه پزشکی ارائه نمی‌کند."
    )

    if "sport" not in existing:
        data["topics"].append(sport)

    if "health" not in existing:
        data["topics"].append(health)

    save(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def fix_data_ids():
    path = DOCS / "metatya-data.js"
    text = read(path)

    text = replace_once(
        text,
        'id: "stocks"',
        'id: "bourse"',
        "شناسه stocks"
    )

    text = replace_once(
        text,
        'id: "personal-finance"',
        'id: "finance"',
        "شناسه personal-finance"
    )

    save(path, text)


def fix_admin():
    path = DOCS / "metatya-admin-content.html"
    text = read(path)

    text = replace_once(
        text,
        '<meta name="description" content="پنل مدیریت محتوای آموزشی پلتفرم Metatya">',
        '<meta name="description" content="پنل مدیریت محتوای آموزشی پلتفرم Metatya">\n'
        '  <meta name="robots" content="noindex, nofollow, noarchive">',
        "متای robots پنل"
    )

    text = replace_once(
        text,
        '{ id: "stocks", name: "بورس و سهام" }',
        '{ id: "bourse", name: "بورس و سهام" }',
        "شناسه بورس پنل"
    )

    text = replace_once(
        text,
        '{ id: "personal-finance", name: "مدیریت مالی شخصی" }',
        '{ id: "finance", name: "مدیریت مالی شخصی" }',
        "شناسه مالی شخصی پنل"
    )

    old = '''return parsed.filter(item =>
        item &&
        typeof item.id === "string" &&
        typeof item.title === "string" &&
        typeof item.category === "string"
      );'''

    new = '''return parsed.filter(item =>
        item &&
        typeof item.id === "string" &&
        typeof item.title === "string" &&
        typeof item.category === "string"
      ).map(item => ({
        ...item,
        category: item.category === "stocks" ? "bourse" :
          item.category === "personal-finance" ? "finance" :
          item.category
      }));'''

    text = replace_once(
        text, old, new, "مهاجرت داده‌های قدیمی پنل"
    )

    save(path, text)


def fix_home():
    path = DOCS / "metatya-home.html"
    text = read(path)

    old = '''محصولات با سطح امکانات متفاوت؛ جزئیات و شرایط دریافت هر نسخه
          باید پیش از عرضه نهایی مشخص و آزمایش شوند.'''

    new = '''هر محصول برای نیاز و سطح متفاوتی طراحی شده است؛
          جزئیات امکانات و شرایط دریافت در مسیر اختصاصی همان محصول ارائه می‌شود.'''

    text = replace_once(
        text, old, new, "حذف یادداشت داخلی محصولات"
    )

    save(path, text)


def fix_topic_router():
    path = DOCS / "topic.html"
    text = read(path)

    old = "const slug = new URLSearchParams(location.search).get('t') || 'forex';"

    new = """const requestedSlug =
    new URLSearchParams(location.search).get('t') || 'forex';

  const slugAliases = {
    stocks: 'bourse',
    'personal-finance': 'finance'
  };

  const slug = slugAliases[requestedSlug] || requestedSlug;"""

    text = replace_once(
        text, old, new, "پشتیبانی شناسه‌های قدیمی"
    )

    old_sport = (
        "const sp = el('a', '', 'ورزش'); "
        "sp.href = 'sport.html'; chips.appendChild(sp);"
    )

    new_sport = """if (!(cfg.topics || []).some(x => x.slug === 'sport')) {
      const sp = el('a', '', 'ورزش');
      sp.href = 'topic.html?t=sport';
      chips.appendChild(sp);
    }"""

    text = replace_once(
        text, old_sport, new_sport, "جلوگیری از لینک تکراری ورزش"
    )

    save(path, text)


def fix_index():
    path = DOCS / "index.html"
    text = read(path)

    text = replace_once(
        text,
        'href="sport.html">',
        'href="topic.html?t=sport">',
        "مسیر یکپارچه ورزش"
    )

    save(path, text)


def fix_telegram_links():
    pattern = re.compile(
        r"https?://t\.me/maytya(?:fx)?/?",
        re.IGNORECASE
    )

    extensions = {".html", ".js", ".json", ".css"}

    for path in DOCS.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue

        try:
            original = read(path)
        except UnicodeDecodeError:
            continue

        updated = pattern.sub(
            "https://t.me/Maytyafx",
            original
        )

        if updated != original:
            save(path, updated)


def create_pillar_page():
    path = DOCS / "pillar.html"

    if path.exists():
        text = read(path)
        if "MetatyaData.getPillar" in text:
            return

    html = r'''<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#050807">
<meta name="description" content="مسیرهای آموزشی Metatya">
<meta name="robots" content="index,follow">
<title>مسیر آموزشی | Metatya</title>
<link rel="stylesheet" href="metatya-core.css">
<link rel="stylesheet" href="metatya-components.css">
<style>
body{background:#050807;color:#edf5ef;font-family:Vazirmatn,Tahoma,sans-serif}
.pillar-wrap{width:min(900px,92%);margin:70px auto}
.pillar-panel{padding:clamp(22px,5vw,48px);border:1px solid rgba(0,255,157,.2);border-radius:24px;background:linear-gradient(145deg,#101b16,#070d0a)}
.pillar-icon{font-size:48px}
.pillar-kicker{color:#00ff9d;font-size:12px;font-weight:800;letter-spacing:1px}
h1{font-size:clamp(28px,5vw,44px);margin:12px 0}
p{color:#aab8ae;line-height:2}
.pillar-meta{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}
.pillar-meta span{border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:5px 12px;font-size:12px}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:28px}
.actions a{padding:12px 18px;border-radius:12px;text-decoration:none;font-weight:800}
.primary{background:#00ff9d;color:#03110a}
.secondary{border:1px solid rgba(255,255,255,.18);color:#edf5ef}
#error{color:#ff8792}
</style>
</head>
<body>
<main class="pillar-wrap">
  <a href="metatya-home.html">← بازگشت به Metatya</a>
  <section class="pillar-panel" aria-live="polite">
    <div class="pillar-kicker">METATYA LEARNING PATH</div>
    <div class="pillar-icon" id="icon">◈</div>
    <h1 id="title">در حال بارگذاری مسیر آموزشی…</h1>
    <p id="description"></p>
    <div class="pillar-meta" id="tracks"></div>
    <p id="error" role="status"></p>
    <div class="actions" id="actions" hidden>
      <a class="primary" id="topicLink" href="#">مطالعه محتوای این حوزه</a>
      <a class="secondary" href="metatya-home.html#pillars">مشاهده همه حوزه‌ها</a>
    </div>
  </section>
</main>
<script src="metatya-data.js"></script>
<script>
(function(){
  "use strict";

  const aliases = {
    stocks: "bourse",
    "personal-finance": "finance"
  };

  const params = new URLSearchParams(location.search);
  const rawId = params.get("id") || "";
  const id = aliases[rawId] || rawId;
  const data = window.MetatyaData;
  const item = data && data.getPillar(id);
  const $ = id => document.getElementById(id);

  if (!item) {
    $("title").textContent = "مسیر آموزشی پیدا نشد";
    $("error").textContent = "این مسیر وجود ندارد یا شناسه آن معتبر نیست.";
    return;
  }

  document.title = item.title + " | Metatya";
  $("icon").textContent = item.icon || "◈";
  $("title").textContent = item.title;
  $("description").textContent = item.description;

  (item.tracks || []).forEach(track => {
    const tag = document.createElement("span");
    tag.textContent = track;
    $("tracks").appendChild(tag);
  });

  $("topicLink").href =
    "topic.html?t=" + encodeURIComponent(id);

  $("actions").hidden = false;
})();
</script>
</body>
</html>'''

    save(path, html)


def verify():
    cfg = json.loads(read(DOCS / "topics.json"))
    slugs = {item["slug"] for item in cfg["topics"]}

    required = {
        "forex", "crypto", "bourse", "finance",
        "sport", "health", "education", "law",
        "psychology", "ai", "privacy"
    }

    missing = required - slugs

    if missing:
        ERRORS.append(
            "موضوعات مفقود در topics.json: " + ", ".join(sorted(missing))
        )

    data = read(DOCS / "metatya-data.js")
    if 'id: "stocks"' in data or 'id: "personal-finance"' in data:
        ERRORS.append("شناسه قدیمی هنوز در metatya-data.js وجود دارد.")

    admin = read(DOCS / "metatya-admin-content.html")
    if 'name="robots" content="noindex, nofollow, noarchive"' not in admin:
        ERRORS.append("متای noindex پنل مدیریت پیدا نشد.")

    home = read(DOCS / "metatya-home.html")
    if "باید پیش از عرضه نهایی مشخص و آزمایش شوند" in home:
        ERRORS.append("یادداشت داخلی هنوز در صفحه اصلی وجود دارد.")

    if not (DOCS / "pillar.html").exists():
        ERRORS.append("صفحه pillar.html ساخته نشده است.")


def main():
    if not DOCS.exists():
        raise SystemExit("پوشه docs پیدا نشد؛ اسکریپت را از مخزن اجرا کن.")

    fix_topics()
    fix_data_ids()
    fix_admin()
    fix_home()
    fix_topic_router()
    fix_index()
    fix_telegram_links()
    create_pillar_page()
    verify()

    print("\n=== METATYA REPAIR REPORT ===")

    for item in CHANGES:
        print("[UPDATED]", item)

    for item in ERRORS:
        print("[ERROR]", item)

    if ERRORS:
        raise SystemExit(
            "\nبرخی بررسی‌ها ناموفق بودند؛ قبل از انتشار اصلاح کن."
        )

    print("\nSUCCESS: اصلاحات محلی اعمال و بررسی اولیه موفق شد.")
    print("توجه: هنوز باید تست مرورگر و انتشار GitHub Pages انجام شود.")


if __name__ == "__main__":
    main()
