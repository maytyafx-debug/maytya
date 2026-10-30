"""ساخت پکیج‌های اختصاصی VIP به‌صورت PDF و آپلود خصوصی به Supabase Storage.

خروجی‌ها داخل docs/ نیستند؛ پس GitHub Pages آن‌ها را منتشر نمی‌کند و commit هم نمی‌شوند.
فایل‌ها فقط از طریق ربات (Worker با کلید سرویس) برای مشتری پرداخت‌کننده فرستاده می‌شوند.
"""
import os, json, html, shutil, urllib.request, urllib.error

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
import arabic_reshaper
from bidi.algorithm import get_display

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")
DATA = os.path.join(REPO, "docs", "content.json")
OUT_DIR = os.path.join(REPO, "private_packs")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_CANDIDATES = [
    os.environ.get("FONT_PATH") or "",
    os.path.join(REPO, "assets", "fonts", "Vazirmatn-Regular.ttf"),
    os.path.join(REPO, "assets", "Fonts", "DejaVuSans.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if p and os.path.exists(p) and os.path.getsize(p) > 50_000), None)
if not FONT_PATH:
    raise SystemExit("فونت فارسی پیدا نشد؛ PDF ساخته نشد.")
pdfmetrics.registerFont(TTFont("Fa", FONT_PATH))

def fa(text):
    """متن فارسی را برای نمایش درست در PDF آماده می‌کند (اتصال حروف + راست‌به‌چپ)."""
    return get_display(arabic_reshaper.reshape(str(text or "")))

ACCENT = HexColor("#1F6F63")
S_TITLE = ParagraphStyle("t", fontName="Fa", fontSize=24, leading=34, alignment=TA_CENTER, textColor=ACCENT)
S_SUB = ParagraphStyle("s", fontName="Fa", fontSize=11, leading=18, alignment=TA_CENTER, textColor=HexColor("#555555"))
S_TAG = ParagraphStyle("g", fontName="Fa", fontSize=9, leading=14, alignment=TA_RIGHT, textColor=ACCENT)
S_H = ParagraphStyle("h", fontName="Fa", fontSize=14, leading=24, alignment=TA_RIGHT, textColor=HexColor("#0F241F"), spaceBefore=10)
S_BODY = ParagraphStyle("b", fontName="Fa", fontSize=11, leading=20, alignment=TA_RIGHT, textColor=HexColor("#222222"))
S_FOOT = ParagraphStyle("f", fontName="Fa", fontSize=8.5, leading=14, alignment=TA_CENTER, textColor=HexColor("#777777"))

DISCLAIMER = "این محتوا آموزشی است و توصیه‌ی سرمایه‌گذاری نیست. هیچ نتیجه‌ی مالی تضمین نمی‌شود."

def build_pdf(path, name, items):
    story = [Spacer(1, 40),
             Paragraph(fa(html.escape(name)), S_TITLE),
             Spacer(1, 6),
             Paragraph(fa("پکیج اختصاصی Metatya"), S_SUB),
             Spacer(1, 14), HRFlowable(width="100%", color=ACCENT, thickness=1.5), Spacer(1, 16)]
    for it in items:
        tab = html.escape(str(it.get("tab", "")))
        title = html.escape(str(it.get("title", "")))
        body = html.escape(str(it.get("body", "")))
        if tab:
            story.append(Paragraph(fa(tab), S_TAG))
        story.append(Paragraph(fa(title), S_H))
        story.append(Paragraph(fa(body), S_BODY))
        story.append(Spacer(1, 6))
    story += [Spacer(1, 24), HRFlowable(width="100%", color=HexColor("#DDDDDD"), thickness=0.8), Spacer(1, 10),
              Paragraph(fa(DISCLAIMER), S_FOOT), Paragraph("Metatya", S_FOOT)]
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=56, rightMargin=56, topMargin=56, bottomMargin=56,
                            title=name, author="Metatya")
    doc.build(story)

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

made = []
for key, sec in data["sections"].items():
    out = os.path.join(OUT_DIR, f"{key}-pack.pdf")
    build_pdf(out, sec["name"], sec["items"])
    made.append(out)
    print("PDF ساخته شد:", os.path.basename(out))

SB_URL = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or ""
if not (SB_URL and SB_KEY):
    print("هشدار: SUPABASE_URL یا SUPABASE_SERVICE_KEY تنظیم نیست؛ فایل‌ها فقط محلی ساخته شدند و ربات نمی‌تواند بفرستد.")
else:
    failed = []
    for path in made:
        name = os.path.basename(path)
        with open(path, "rb") as f:
            body = f.read()
        req = urllib.request.Request(
            f"{SB_URL}/storage/v1/object/paid-packs/packs/{name}", data=body, method="POST",
            headers={"Authorization": f"Bearer {SB_KEY}", "apikey": SB_KEY,
                     "Content-Type": "application/pdf", "x-upsert": "true"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print("آپلود شد (خصوصی):", name, r.status)
        except urllib.error.HTTPError as e:
            print("آپلود نشد:", name, e.code, e.read()[:200])
            failed.append(name)

if "failed" in globals() and failed:
    raise SystemExit(f"آپلود {len(failed)} فایل شکست خورد؛ کلید SUPABASE_SERVICE_KEY باید secret key (service_role) باشد.")
print("بسته‌های اختصاصی ساخته شدند.")
