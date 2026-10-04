"""ساخت ویدیوی ۱۰ ثانیه‌ای عمودی (۱۰۸۰x۱۹۲۰) از short_script هر بازار -> out/*.mp4
نیاز: pillow arabic-reshaper python-bidi + ffmpeg + فونت فارسی (FONT_PATH)"""
import os, json, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.join(os.path.dirname(__file__), "..")
FONT = os.environ.get("FONT_PATH", "Vazirmatn-Regular.ttf")
W, H = 1080, 1920
def fa(s): return get_display(arabic_reshaper.reshape(s))

def frame(lines, path, brand="Metatya"):
    im = Image.new("RGB", (W, H), (15, 36, 31))
    d = ImageDraw.Draw(im)
    big, small = ImageFont.truetype(FONT, 78), ImageFont.truetype(FONT, 44)
    y = 560
    for ln in lines:
        for part in textwrap.wrap(ln, 22):
            w = d.textlength(fa(part), font=big)
            d.text(((W - w) / 2, y), fa(part), font=big, fill=(238, 243, 241)); y += 110
    bw = d.textlength(brand, font=small)
    d.text(((W - bw) / 2, H - 200), brand, font=small, fill=(192, 138, 46))
    im.save(path)

def main():
    data = json.load(open(os.path.join(ROOT, "docs", "content.json"), encoding="utf-8"))
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
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
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-t", "10", "-r", "30",
                        "-pix_fmt", "yuv420p", os.path.join(ROOT, "out", f"{key}_short.mp4")], check=True)
        it = items[0]; site = os.environ.get("SITE_URL", "")
        open(os.path.join(ROOT, "out", f"{key}_upload.txt"), "w", encoding="utf-8").write(
            f"عنوان: {it['title']} | Metatya\n\nتوضیح:\n{it['body'][:300]}\n\nتحلیل کامل و آموزش بیشتر: {site}\nتلگرام: https://t.me/maytya\nاینستاگرام: https://instagram.com/maytyafx\n\n#Metatya #فارکس #کریپتو #بورس #تحلیل_بازار\n⚠️ توصیه سرمایه‌گذاری نیست.\n")
        print("ساخته شد:", key)
main()
