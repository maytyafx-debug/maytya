"""ساخت ویدیوی ۱۰ ثانیه‌ای عمودی (۱۰۸۰x۱۹۲۰) از short_script هر بازار -> out/*.mp4 و out/*_upload.txt
رندر فارسی: اگر Pillow با RAQM (حرف‌چین و راست‌به‌چپ داخلی) در دسترس باشد از همان استفاده می‌شود؛
وگرنه arabic-reshaper + python-bidi. فونت: FONT_PATH یا دانلود Vazirmatn یا فونت‌های سیستمی دارای حروف فارسی.
اجرای آزمایش: python scripts/make_short.py --selftest"""
import os, sys, json, subprocess, textwrap, urllib.request, shutil
from PIL import Image, ImageDraw, ImageFont, features

ROOT = os.path.join(os.path.dirname(__file__), "..")
W, H = 1080, 1920
RAQM = features.check("raqm")
FONT_URLS = [
    "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/npm/vazirmatn@33.0.3/fonts/ttf/Vazirmatn-Regular.ttf",
]
SYSTEM_FALLBACKS = ["Vazirmatn", "Noto Sans Arabic", "Noto Naskh Arabic", "DejaVu Sans"]

def _ok_font(path):
    try:
        ImageFont.truetype(path, 40); return os.path.getsize(path) > 50_000
    except Exception:
        return False

def find_font():
    for p in (os.environ.get("FONT_PATH"), os.path.join(ROOT, "assets", "fonts", "Vazirmatn-Regular.ttf")):
        if p and os.path.exists(p) and _ok_font(p): return p
    dst = os.path.join(ROOT, "out", "Vazirmatn-Regular.ttf")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if _ok_font(dst): return dst
    for u in FONT_URLS:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(dst, "wb") as f: shutil.copyfileobj(r, f)
            if _ok_font(dst): print("فونت دانلود شد:", u); return dst
        except Exception as e:
            print("دانلود فونت ناموفق:", u[:60], e)
    for fam in SYSTEM_FALLBACKS:
        try:
            out = subprocess.run(["fc-match", "-f", "%{file}", fam + ":lang=fa"], capture_output=True, text=True).stdout.strip()
            if out and _ok_font(out): print("فونت سیستمی:", out); return out
        except Exception: pass
    sys.exit("هیچ فونت فارسی پیدا نشد؛ FONT_PATH را تنظیم کنید")

FONT = find_font()

if not RAQM:
    import arabic_reshaper
    try: from bidi import get_display            # python-bidi >= 0.5
    except ImportError: from bidi.algorithm import get_display
    _R = arabic_reshaper.ArabicReshaper(configuration={"delete_harakat": True})
    def prep(s): return get_display(_R.reshape(s))
else:
    def prep(s): return s                            # RAQM خودش حرف‌چینی و جهت را انجام می‌دهد

def font_at(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM if RAQM else ImageFont.Layout.BASIC)

def draw_center(d, y, text, fnt, fill):
    kw = {"direction": "rtl", "language": "fa"} if RAQM else {}
    d.text((W / 2, y), prep(text), font=fnt, fill=fill, anchor="ma", **kw)

def wrap_px(d, text, fnt, maxw):
    """شکستن خط بر اساس عرض واقعی پیکسلی (نه تعداد حرف)"""
    kw = {"direction": "rtl", "language": "fa"} if RAQM else {}
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if cur and d.textlength(prep(t), font=fnt, **kw) > maxw: lines.append(cur); cur = w
        else: cur = t
    return lines + ([cur] if cur else [])

def frame(lines, path, brand="Metatya"):
    im = Image.new("RGB", (W, H), (15, 36, 31)); d = ImageDraw.Draw(im)
    big, small = font_at(80), font_at(44)
    rows = [p for ln in lines for p in wrap_px(d, ln, big, W - 200)]
    y = H // 2 - len(rows) * 62
    for part in rows:
        draw_center(d, y, part, big, (238, 243, 241)); y += 124
    d.text((W / 2, H - 200), brand, font=small, fill=(192, 138, 46), anchor="ma")
    im.save(path)

def main():
    if "--selftest" in sys.argv:
        os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
        frame(["یورو/دلار زیر ۱.۱۳۱۲ آمد", "شاخص کل بورس ۷٬۷۶۶٬۵۴۰ واحد", "Bitcoin بالای 86,000 دلار"], os.path.join(ROOT, "out", "selftest.png"))
        print("selftest.png ساخته شد | RAQM:", RAQM); return
    data = json.load(open(os.path.join(ROOT, "docs", "content.json"), encoding="utf-8"))
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    site = os.environ.get("SITE_URL", "")
    for key in ("forex", "crypto", "bourse"):
        items = data["sections"].get(key, {}).get("items", [])
        if not items: continue
        frames = []
        for i, ln in enumerate(items[0]["short_script"][:3]):
            p = os.path.join(ROOT, "out", f"{key}_{i}.png"); frame([ln], p); frames.append(p)
        lst = os.path.join(ROOT, "out", f"{key}.txt")
        with open(lst, "w") as f:
            for p in frames: f.write(f"file '{os.path.abspath(p)}'\nduration 3.3\n")
            f.write(f"file '{os.path.abspath(frames[-1])}'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-t", "10", "-r", "30",
                        "-pix_fmt", "yuv420p", os.path.join(ROOT, "out", f"{key}_short.mp4")], check=True)
        it = items[0]
        open(os.path.join(ROOT, "out", f"{key}_upload.txt"), "w", encoding="utf-8").write(
            f"عنوان: {it['title']} | Metatya\n\nتوضیح:\n{it['body'][:300]}\n\nتحلیل کامل و آموزش بیشتر: {site}\nتلگرام: https://t.me/maytya\nاینستاگرام: https://instagram.com/maytyafx\n\n#Metatya #فارکس #کریپتو #بورس #تحلیل_بازار\n⚠️ توصیه سرمایه‌گذاری نیست.\n")
        print("ساخته شد:", key)

main()
