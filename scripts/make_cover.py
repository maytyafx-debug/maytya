"""ساخت تصویر پیش‌نمایش پک رایگان (۱۰۸۰x۱۳۵۰) با عکس بنیان‌گذار از index.html -> docs/downloads/free-pack-preview.png
اجرا: FONT_PATH=<فونت فارسی> python scripts/make_cover.py   (اعداد داخل تصویر نمونه‌اند، نه پرتفوی واقعی)"""
import re, base64, io, os, sys
sys.argv = ["x"]; sys.path.insert(0, os.path.dirname(__file__))
import make_short as m
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(__file__), "..")
h = open(os.path.join(ROOT, "docs", "index.html"), encoding="utf-8").read()
ava = Image.open(io.BytesIO(base64.b64decode(re.search(r'founder-avatar"><img[^>]*src="data:image/[a-z]+;base64,([A-Za-z0-9+/=]+)"', h).group(1)))).convert("RGB")
W, H = 1080, 1350
im = m.gradient((8, 24, 21), (26, 96, 86)).resize((W, H))
for (x, y, s, c, a) in ((120, 180, 420, (255, 200, 87), .35), (900, 520, 520, (120, 220, 200), .28), (300, 1150, 480, (255, 200, 87), .22)):
    g = m.glow(s, c, a); im.paste(g, (x - s // 2, y - s // 2), g)
d = ImageDraw.Draw(im); REG = os.environ["FONT_PATH"]; BOLD = REG.replace("Sans.ttf", "Sans-Bold.ttf") if os.path.exists(REG.replace("Sans.ttf", "Sans-Bold.ttf")) else REG
F = lambda sz, b=False: ImageFont.truetype(BOLD if b else REG, sz)
def rtl(xr, y, text, font, fill, center=False):
    t = m.prep(text); w = d.textlength(t, font=font, **m.KW); d.text(((W - w) / 2 if center else xr - w, y), t, font=font, fill=fill, **m.KW); return w
s = min(ava.size); ava = ava.crop(((ava.width - s) // 2, (ava.height - s) // 2, (ava.width + s) // 2, (ava.height + s) // 2)).resize((170, 170), Image.LANCZOS)
mk = Image.new("L", (170, 170), 0); ImageDraw.Draw(mk).ellipse([0, 0, 169, 169], fill=255)
rg = Image.new("RGB", (190, 190), (255, 200, 87)); rm = Image.new("L", (190, 190), 0); ImageDraw.Draw(rm).ellipse([0, 0, 189, 189], fill=255)
im.paste(rg, (W - 250, 60), rm); im.paste(ava, (W - 240, 70), mk)
rtl(W - 274, 95, "آیت قمری", F(46, True), (238, 243, 241)); rtl(W - 274, 160, "بنیان‌گذار Metatya", F(32), (255, 200, 87)); d.text((60, 92), "Metatya", font=F(54, True), fill=(255, 200, 87))
rtl(0, 300, "ردیاب رایگان پرتفوی بورس", F(66, True), (255, 255, 255), True)
rtl(0, 400, "ارزش خالص، سود و زیان، وزن هر سهم و هشدار تمرکز؛ خودکار", F(34), (200, 225, 218), True)
px, py, pw, ph = 190, 500, 700, 650
d.rounded_rectangle([px - 14, py - 14, px + pw + 14, py + ph + 14], radius=64, fill=(14, 22, 20)); d.rounded_rectangle([px, py, px + pw, py + ph], radius=52, fill=(240, 244, 243))
rtl(px + pw - 34, py + 26, "نماد / تعداد", F(26), (110, 125, 120)); rtl(px + 400, py + 26, "آخرین قیمت", F(26), (110, 125, 120)); rtl(px + 190, py + 26, "ارزش و سود", F(26), (110, 125, 120))
rows = [("نمونه ۱", "1,000", "12,000", "11,880,000", "+1,880,000", "+18.8%", True), ("نمونه ۲", "500", "22,000", "10,903,200", "-1,096,800", "-9.1%", False), ("نمونه ۳", "200", "90,000", "17,841,600", "+1,841,600", "+11.5%", True)]
for i, (n, q, pr, val, pl, pc, up) in enumerate(rows):
    y = py + 86 + i * 160; d.rounded_rectangle([px + 18, y, px + pw - 18, y + 142], radius=26, fill=(255, 255, 255), outline=(222, 230, 228), width=2)
    col = (24, 160, 100) if up else (210, 70, 60)
    d.ellipse([px + pw - 60, y + 24, px + pw - 38, y + 46], fill=col); rtl(px + pw - 72, y + 14, n, F(36, True), (20, 30, 28)); rtl(px + pw - 48, y + 82, q, F(30), (60, 70, 68))
    d.text((px + 330, y + 22), pr, font=F(34), fill=(30, 40, 38)); d.text((px + 44, y + 16), val, font=F(32, True), fill=(30, 40, 38)); d.text((px + 44, y + 82), f"{pl} ({pc})", font=F(27, True), fill=col)
rtl(0, py + ph - 70, "اعداد نمونه‌اند • قیمت‌ها را خودت وارد می‌کنی", F(26), (120, 135, 130), True)
d.rounded_rectangle([20, 700, 170, 776], radius=34, fill=(255, 200, 87)); t = m.prep("رایگان"); d.text((95 - d.textlength(t, font=F(38, True), **m.KW) / 2, 712), t, font=F(38, True), fill=(26, 20, 5), **m.KW)
d.rounded_rectangle([90, 1205, W - 90, 1290], radius=44, fill=(255, 200, 87)); rtl(0, 1220, "دانلود رایگان · لینک در بایو · t.me/maytya", F(38, True), (26, 20, 5), True)
rtl(0, 1308, "آموزشی است؛ توصیه‌ی خرید یا فروش نیست", F(24), (160, 185, 178), True)
out = os.path.join(ROOT, "docs", "downloads", "free-pack-preview.png"); im.save(out, optimize=True); print("ساخته شد:", out)
