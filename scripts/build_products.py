"""Build Metatya's real, educational LITE/PRO downloads.

All workbooks are learning and reflection tools. They do not provide trade
signals, position sizing, investment recommendations, body-weight targets,
calorie restriction, or medical/psychological diagnosis.
"""
from pathlib import Path
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "downloads"
PRIVATE_OUT = ROOT / "out" / "private-products"
FONT = ROOT / "assets" / "fonts" / "Vazirmatn-Regular.ttf"
OUT.mkdir(parents=True, exist_ok=True)
PRIVATE_OUT.mkdir(parents=True, exist_ok=True)

import arabic_reshaper
from bidi.algorithm import get_display

def rtl(value):
    return get_display(arabic_reshaper.reshape(str(value)))

if not FONT.exists():
    raise RuntimeError("فونت Vazirmatn برای ساخت PDF فارسی در دسترس نیست")
pdfmetrics.registerFont(TTFont("Vazirmatn", str(FONT)))
PDF_FONT = "Vazirmatn"

NAVY = "14251F"
GREEN = "1F6F63"
GOLD = "C08A2E"
PALE = "EAF2EF"
WHITE = "FFFFFF"
LINE = "D7E2DD"

def setup_sheet(ws, title, headers, rows, widths=None):
    ws.sheet_view.rightToLeft = True
    ws.freeze_panes = "A2"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.append([title])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws["A1"].font = Font(name="Aptos", size=14, bold=True, color=WHITE)
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws["A1"].alignment = Alignment(horizontal="right")
    ws.append(headers)
    for cell in ws[2]:
        cell.font = Font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=GREEN)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(bottom=Side(style="thin", color=LINE))
    for row in rows:
        ws.append(row)
    for row in ws.iter_rows(min_row=3):
        for cell in row:
            cell.alignment = Alignment(horizontal="right", vertical="top", wrap_text=True)
            if cell.row % 2:
                cell.fill = PatternFill("solid", fgColor="F5F8F6")
    ws.row_dimensions[1].height = 28
    ws.row_dimensions[2].height = 34
    if widths:
        for idx, width in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = width
    ws.auto_filter.ref = f"A2:{get_column_letter(len(headers))}{max(2, ws.max_row)}"

def add_intro(wb, title, description, audience, safety):
    ws = wb.active
    ws.title = "راهنما"
    ws.sheet_view.rightToLeft = True
    rows = [
        ["محصول", title],
        ["نسخه", "LITE / PRO — ابزار آموزشی Metatya"],
        ["هدف", description],
        ["مناسب برای", audience],
        ["روش استفاده", "هر بار فقط داده و مشاهده واقعی یا سناریوی فرضی را ثبت کن؛ منبع و تاریخ را بنویس و بعداً مرور کن."],
        ["محدودیت", safety],
        ["حریم خصوصی", "اطلاعات هویتی، رمز، کد یک‌بارمصرف یا داده محرمانه را در فایل وارد نکن."],
        ["تاریخ ساخت", date.today().isoformat()],
    ]
    for row in rows:
        ws.append(row)
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 100
    for cell in ws["A"]:
        cell.font = Font(bold=True, color=GREEN)
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal="right", vertical="top", wrap_text=True)
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"

def workbook_risk(tier, filename):
    wb = Workbook()
    count = 20 if tier == "LITE" else 200
    add_intro(
        wb, f"دفترچه سواد مالی و ثبت مشاهده — {tier}",
        "ثبت آموزشی فرضیه، منبع، شواهد، عدم قطعیت و بازنگری رفتار؛ بدون سیگنال یا محاسبه معامله.",
        "یادگیرنده‌ای که می‌خواهد فرایند فکر و کیفیت منابع را مرور کند.",
        "این فایل توصیه سرمایه‌گذاری، خریدوفروش، قیمت ورود و خروج یا محاسبه حجم معامله ارائه نمی‌کند."
    )
    ws = wb.create_sheet("ثبت مشاهده")
    headers = ["تاریخ", "موضوع/دارایی برای مطالعه", "بازه یا زمینه", "منبع اطلاعات", "مشاهده بی‌طرفانه", "فرضیه آموزشی", "شواهد موافق", "شواهد مخالف", "عدم قطعیت", "حالت ذهنی", "یادداشت مرور"]
    rows = [[""] * len(headers) for _ in range(count)]
    setup_sheet(ws, "ثبت مشاهده و یادگیری", headers, rows, [14,24,18,30,34,34,30,30,25,18,34])
    dv = DataValidation(type="list", formula1='"آرام،کنجکاو،نامطمئن،خسته،هیجان‌زده"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(f"J3:J{count+2}")
    review = wb.create_sheet("مرور دوره‌ای")
    setup_sheet(review, "مرور کیفیت فرایند", ["پرسش", "یادداشت"], [
        ["آیا منبع اولیه و تاریخ آن را ثبت کردم؟", ""],
        ["کدام فرضیه با شواهد ناسازگار بود؟", ""],
        ["چه چیزی را هنوز نمی‌دانم؟", ""],
        ["آیا نظر شخصی را از داده جدا کردم؟", ""],
        ["در مرور بعدی چه مهارتی را تمرین می‌کنم؟", ""],
    ], [55,100])
    wb.save((OUT if tier == "LITE" else PRIVATE_OUT) / filename)

def workbook_bourse(tier, filename):
    wb = Workbook()
    count = 20 if tier == "LITE" else 200
    add_intro(
        wb, f"دفترچه مطالعه گزارش‌های شرکت — {tier}",
        "تمرین خواندن گزارش‌های عمومی شرکت‌ها و مقایسه شاخص‌های حسابداری با ذکر منبع.",
        "یادگیرنده سواد مالی و تحلیل گزارش‌های عمومی.",
        "این ابزار پرتفوی شخصی، سیگنال، رتبه‌بندی یا توصیه خریدوفروش سهم نیست."
    )
    ws = wb.create_sheet("مطالعه گزارش")
    headers = ["نام شرکت/نماد برای مطالعه", "دوره گزارش", "منبع رسمی", "درآمد گزارش‌شده", "سود عملیاتی", "جریان نقد عملیاتی", "بدهی/تعهدات", "نکته مهم", "محدودیت داده"]
    rows = [[""] * len(headers) for _ in range(count)]
    setup_sheet(ws, "مطالعه گزارش‌های منتشرشده", headers, rows, [28,18,38,20,20,24,20,36,30])
    ws2 = wb.create_sheet("واژه‌نامه")
    setup_sheet(ws2, "واژه‌های پایه", ["اصطلاح", "تعریف آموزشی"], [
        ["درآمد", "ارزش فروش یا خدمات ثبت‌شده در یک دوره؛ با وجه نقد دریافتی یکسان نیست."],
        ["سود عملیاتی", "نتیجه فعالیت اصلی پس از هزینه‌های عملیاتی طبق صورت مالی."],
        ["جریان نقد عملیاتی", "وجه نقد حاصل از فعالیت‌های اصلی در دوره گزارش."],
        ["بدهی", "تعهدات مالی شرکت؛ سررسید و شرایط آن مهم است."],
        ["یادداشت‌های توضیحی", "بخش مکمل صورت‌های مالی برای شناخت جزئیات و مفروضات."],
    ], [28,110])
    wb.save((OUT if tier == "LITE" else PRIVATE_OUT) / filename)

def workbook_fit(tier, filename):
    wb = Workbook()
    count = 7 if tier == "LITE" else 28
    add_intro(
        wb, f"دفترچه مهارت و عادت ورزشی — {tier}",
        "ثبت کیفیت حرکت، مهارت، خواب، آب‌رسانی، احساس و بازیابی؛ بدون وزن‌کشی یا هدف کالری.",
        "افرادی که می‌خواهند عادت‌های حرکتی سالم را با انعطاف پیگیری کنند.",
        "برنامه تمرین شخصی یا پزشکی نیست. فعالیت باید متناسب با سن و شرایط باشد؛ با مربی/سرپرست آگاه هماهنگ کن و در صورت درد یا ناراحتی غیرعادی توقف کن."
    )
    ws = wb.create_sheet("برنامه مهارت")
    headers = ["هفته/روز", "فعالیت دلخواه", "مدت تقریبی (دقیقه)", "مهارت مورد تمرین", "گرم‌کردن انجام شد؟", "کیفیت حرکت ۱ تا ۵", "احساس پس از تمرین", "بازخورد مربی/همراه"]
    rows = [[""] * len(headers) for _ in range(count)]
    setup_sheet(ws, "برنامه انعطاف‌پذیر مهارت", headers, rows, [16,24,20,30,20,20,24,34])
    ws2 = wb.create_sheet("عادت و بازیابی")
    headers2 = ["روز", "کیفیت خواب ۱ تا ۵", "آب‌رسانی مناسب؟", "انرژی ۱ تا ۵", "استراحت کافی؟", "حال عمومی", "یادداشت"]
    rows2 = [[""] * len(headers2) for _ in range(count)]
    setup_sheet(ws2, "عادت‌های پشتیبان", headers2, rows2, [16,22,22,18,20,24,40])
    wb.save((OUT if tier == "LITE" else PRIVATE_OUT) / filename)

def workbook_mind(tier, filename):
    wb = Workbook()
    count = 7 if tier == "LITE" else 21
    add_intro(
        wb, f"دفترچه خودآگاهی و عادت — {tier}",
        "ثبت کوتاه حال عمومی، موقعیت، فکر، پاسخ متعادل و اقدام حمایتی برای شناخت الگوها.",
        "تمرین خودآگاهی و مرور عادت‌های روزمره.",
        "این ابزار تشخیص یا درمان نیست و شدت علائم را ارزیابی نمی‌کند. اگر ناراحتی پایدار یا شدید است، با بزرگسال مورد اعتماد و متخصص سلامت صحبت کن."
    )
    ws = wb.create_sheet("ثبت روزانه")
    headers = ["تاریخ", "حال عمومی با یک واژه", "انرژی ۱ تا ۵", "کیفیت خواب ۱ تا ۵", "اتفاق یا محرک", "فکر خودکار", "نگاه متعادل‌تر", "اقدام حمایتی", "یادداشت"]
    rows = [[""] * len(headers) for _ in range(count)]
    setup_sheet(ws, "ثبت روزانه", headers, rows, [14,24,16,20,34,34,34,30,32])
    ws2 = wb.create_sheet("مرور")
    setup_sheet(ws2, "مرور مهربانانه", ["پرسش", "یادداشت"], [
        ["چه چیزی امروز کمک‌کننده بود؟", ""],
        ["چه موقعیتی انرژی من را گرفت؟", ""],
        ["آیا با خودم منصفانه حرف زدم؟", ""],
        ["از چه کسی می‌توانم حمایت بخواهم؟", ""],
        ["یک عادت کوچک و واقع‌بینانه برای فردا چیست؟", ""],
    ], [55,100])
    wb.save((OUT if tier == "LITE" else PRIVATE_OUT) / filename)

def workbook_biz(tier, filename):
    wb = Workbook()
    count = 10 if tier == "LITE" else 50
    add_intro(
        wb, f"دفترچه مدل کسب‌وکار آموزشی — {tier}",
        "ثبت فرضیه مشتری، هزینه، قیمت فرضی، بازخورد و گام بعدی برای آزمایش کوچک.",
        "یادگیرنده کارآفرینی و طراحی مدل کسب‌وکار.",
        "اعداد صرفاً فرضی یا ورودی آموزشی‌اند؛ نتیجه یا درآمد تضمین نمی‌شود. برای فعالیت واقعی، قوانین و محدودیت‌های سنی/محلی را بررسی کن."
    )
    ws = wb.create_sheet("فرضیه مشتری")
    headers = ["گروه مخاطب", "مسئله‌ای که بیان کرده", "راه‌حل پیشنهادی", "شواهد/مصاحبه", "فرضیه قابل آزمون", "نتیجه آزمایش", "گام بعدی"]
    rows = [[""] * len(headers) for _ in range(count)]
    setup_sheet(ws, "اعتبارسنجی مسئله", headers, rows, [24,34,34,34,34,30,28])
    ws2 = wb.create_sheet("مدل هزینه")
    setup_sheet(ws2, "سناریوی فرضی سربه‌سر", ["ورودی", "مقدار فرضی", "توضیح"], [
        ["قیمت فرضی هر واحد", 100, "واحد پول دلخواه؛ فقط برای تمرین"],
        ["هزینه متغیر هر واحد", 40, "هزینه مستقیم فرضی"],
        ["هزینه ثابت دوره", 600, "هزینه فرضی یک دوره"],
        ["حاشیه مشارکت", "=B3-B4", "قیمت منهای هزینه متغیر"],
        ["نقطه سربه‌سر (واحد)", '=IF(B6>0,B5/B6,0)', "هزینه ثابت تقسیم بر حاشیه مشارکت؛ فقط مدل آموزشی"],
    ], [34,24,90])
    ws2["B6"].number_format = "0.00"
    ws2["B7"].number_format = "0.00"
    wb.save((OUT if tier == "LITE" else PRIVATE_OUT) / filename)

def build_pdf(filename, title, subtitle, sections):
    path = PRIVATE_OUT / filename
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("FaTitle", parent=styles["Title"], fontName=PDF_FONT, fontSize=18, leading=28, alignment=TA_RIGHT, textColor=colors.HexColor("#14251F"), spaceAfter=12)
    head_style = ParagraphStyle("FaHead", parent=styles["Heading2"], fontName=PDF_FONT, fontSize=13, leading=21, alignment=TA_RIGHT, textColor=colors.HexColor("#1F6F63"), spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle("FaBody", parent=styles["BodyText"], fontName=PDF_FONT, fontSize=10.5, leading=19, alignment=TA_RIGHT, textColor=colors.HexColor("#26352F"), spaceAfter=7)
    story = [Paragraph(rtl(title), title_style), Paragraph(rtl(subtitle), body_style), Spacer(1, 5*mm)]
    for heading, paragraphs in sections:
        story.append(Paragraph(rtl(heading), head_style))
        for paragraph in paragraphs:
            story.append(Paragraph(rtl(paragraph), body_style))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(rtl("Metatya — محتوای آموزشی عمومی. نسخه و قوانین محلی را بررسی کن؛ این راهنما جایگزین متخصص نیست."), body_style))
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm, title=title, author="Metatya")
    doc.build(story)

GUIDES = {
    "risk-guide.pdf": ("راهنمای سواد مالی و ثبت تصمیم", "دفترچه آموزشی برای جداکردن داده، فرضیه، احساس و نتیجه", [
        ("۱. هدف دفترچه", ["این دفترچه برای یادگیری و مرور کیفیت فکر طراحی شده است؛ سیگنال، توصیه خریدوفروش یا محاسبه حجم معامله ارائه نمی‌کند.", "هر مشاهده را با تاریخ و منبع ثبت کن تا بعداً بتوانی آن را بررسی کنی."]),
        ("۲. داده در برابر فرضیه", ["آنچه واقعاً دیده‌ای را از برداشتی که درباره آن داری جدا بنویس. یک فرضیه خوب باید شواهد مخالف و امکان ردشدن داشته باشد."]),
        ("۳. شناخت عدم قطعیت", ["داده ناقص، تأخیر زمانی و تفاوت منابع می‌توانند برداشت را تغییر دهند. اگر پاسخ را نمی‌دانی، صریحاً بنویس: هنوز مشخص نیست."]),
        ("۴. بازنگری رفتار", ["پس از مدتی بررسی کن چه زمانی عجله، خستگی یا هیجان روی قضاوت اثر گذاشته است. هدف سرزنش نیست؛ شناخت الگوهاست."]),
    ]),
    "bourse-guide.pdf": ("راهنمای مطالعه گزارش‌های شرکت", "تمرین سواد مالی و خواندن اطلاعات عمومی شرکت‌ها", [
        ("۱. از منبع رسمی شروع کن", ["گزارش را از سامانه یا وب‌سایت رسمی منتشرکننده دریافت کن و دوره گزارش را ثبت کن. تصویر بریده‌شده یا پیام شبکه اجتماعی به‌تنهایی منبع کافی نیست."]),
        ("۲. چند شاخص را کنار هم بخوان", ["درآمد، سود عملیاتی، جریان نقد عملیاتی و بدهی هر کدام بُعد متفاوتی از فعالیت شرکت را نشان می‌دهند. هیچ عددی به‌تنهایی تصویر کامل نمی‌دهد."]),
        ("۳. مقایسه منصفانه", ["دوره‌های زمانی، واحد اندازه‌گیری و روش حسابداری باید قابل مقایسه باشند. تفاوت صنعت‌ها نیز مقایسه مستقیم را محدود می‌کند."]),
        ("۴. مرز ابزار", ["این فایل برای مطالعه آموزشی است؛ رتبه‌بندی یا توصیه خریدوفروش سهم نمی‌دهد. برای تصمیم‌های مالی واقعی از متخصص مجاز و منابع رسمی کمک بگیر."]),
    ]),
    "fit-guide.pdf": ("راهنمای عادت و مهارت ورزشی", "پیگیری انعطاف‌پذیر فعالیت، مهارت و بازیابی بدون وزن‌محوری", [
        ("۱. هدف مهارتی انتخاب کن", ["هدف را به کیفیت حرکت، یادگیری یک مهارت یا لذت از فعالیت پیوند بده؛ نه مقایسه بدن یا عدد ترازو."]),
        ("۲. به‌تدریج پیش برو", ["فعالیت را با تجربه و شرایط خود هماهنگ کن. افزایش ناگهانی فشار لازم نیست؛ استراحت بخشی از تمرین است."]),
        ("۳. عادت‌های پشتیبان", ["خواب کافی، آب‌رسانی، تنوع فعالیت و روزهای سبک به تداوم کمک می‌کنند. از رژیم محدودکننده یا تمرین برای جبران غذا استفاده نکن."]),
        ("۴. ایمنی", ["با مربی آگاه و در صورت نیاز سرپرست هماهنگ کن. درد، سرگیجه یا ناراحتی غیرعادی را نادیده نگیر و از متخصص کمک بگیر."]),
    ]),
    "mind-guide.pdf": ("راهنمای خودآگاهی و عادت", "تمرین کوتاه برای شناخت احساس و انتخاب پاسخ متعادل", [
        ("۱. ثبت بدون قضاوت", ["حال عمومی را با یک واژه ثبت کن. لازم نیست هر روز عالی یا پربازده باشی؛ هدف شناخت تجربه است."]),
        ("۲. فکر خودکار و نگاه متعادل", ["یک فکر را بنویس و سپس شواهد موافق، شواهد مخالف و نگاه مهربانانه‌تر را بررسی کن. این تمرین تشخیص یا درمان نیست."]),
        ("۳. عادت کوچک", ["به‌جای تغییر بزرگ، یک اقدام ساده و واقع‌بینانه انتخاب کن؛ مانند آماده‌کردن وسایل مطالعه یا چند دقیقه استراحت از صفحه‌نمایش."]),
        ("۴. حمایت", ["اگر ناراحتی پایدار یا شدید است، تنها نمان و با بزرگسال مورد اعتماد و متخصص سلامت صحبت کن."]),
    ]),
    "biz-guide.pdf": ("راهنمای مدل کسب‌وکار کوچک", "آزمایش فرضیه پیش از صرف هزینه و توسعه", [
        ("۱. مسئله را بشناس", ["با مخاطب احتمالی گفت‌وگو کن و اجازه بده مسئله را با زبان خودش توضیح دهد. از سؤال‌های القایی پرهیز کن."]),
        ("۲. راه‌حل کوچک بساز", ["پیش از ساخت محصول کامل، نمونه ساده‌ای آماده کن و بازخورد واقعی بگیر. علاقه کلامی با تقاضای واقعی یکسان نیست."]),
        ("۳. هزینه و درآمد فرضی", ["هزینه ثابت، هزینه متغیر و قیمت فرضی را جدا ثبت کن. محاسبه سربه‌سر یک مدل آموزشی است و نتیجه بازار را پیش‌بینی نمی‌کند."]),
        ("۴. قانون و اعتماد", ["حریم خصوصی، صداقت در تبلیغ، شرایط سنی و مقررات محل فعالیت را رعایت کن. هیچ مدل ساده‌ای درآمد را تضمین نمی‌کند."]),
    ]),
}

def main():
    builders = [
        (workbook_risk, "Metatya-Trading-Journal-LITE.xlsx", "risk-journal.xlsx"),
        (workbook_bourse, "Metatya-Bourse-LITE.xlsx", "bourse-tracker.xlsx"),
        (workbook_fit, "Metatya-Fit-LITE.xlsx", "fit-program.xlsx"),
        (workbook_mind, "Metatya-Mind-LITE.xlsx", "mind-journal.xlsx"),
        (workbook_biz, "Metatya-Biz-LITE.xlsx", "biz-model.xlsx"),
    ]
    for builder, lite, pro in builders:
        builder("LITE", lite)
        builder("PRO", pro)
    for filename, (title, subtitle, sections) in GUIDES.items():
        build_pdf(filename, title, subtitle, sections)
    expected = [
        "Metatya-Trading-Journal-LITE.xlsx", "Metatya-Bourse-LITE.xlsx",
        "Metatya-Fit-LITE.xlsx", "Metatya-Mind-LITE.xlsx", "Metatya-Biz-LITE.xlsx",
        "risk-journal.xlsx", "bourse-tracker.xlsx", "fit-program.xlsx",
        "mind-journal.xlsx", "biz-model.xlsx", *GUIDES.keys()
    ]
    for name in expected:
        path = (OUT if name.endswith("-LITE.xlsx") else PRIVATE_OUT) / name
        if not path.exists() or path.stat().st_size < 1000:
            raise RuntimeError(f"فایل محصول ساخته نشد یا ناقص است: {name}")
        print(f"OK {name}: {path.stat().st_size} bytes")
    print(f"PRODUCTS_OK={len(expected)}")

if __name__ == "__main__":
    main()
