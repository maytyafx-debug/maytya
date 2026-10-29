import os, json, html, urllib.request, urllib.error

ROOT = os.path.join(os.path.dirname(__file__), "..", "docs")
DATA = os.path.join(ROOT, "content.json")
# خروجی خصوصی: داخل docs نیست، پس GitHub Pages آن را منتشر نمی‌کند و commit هم نمی‌شود.
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "private_packs")
os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

E = html.escape

TPL = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} | Metatya PRO</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  body {{ font-family: 'Vazirmatn', sans-serif; background: #fff; color: #111; padding: 20px; line-height: 2; max-width: 800px; margin: 0 auto; }}
  .cover {{ text-align: center; padding: 60px 0; border-bottom: 2px solid #1F6F63; margin-bottom: 30px; }}
  .cover h1 {{ font-size: 32px; color: #1F6F63; margin-bottom: 10px; }}
  .cover p {{ color: #555; }}
  h2 {{ font-size: 22px; color: #1F6F63; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
  h3 {{ font-size: 18px; margin-top: 20px; color: #0F241F; }}
  p {{ font-size: 15px; text-align: justify; color: #333; }}
  .tag {{ display: inline-block; background: #eef3f1; color: #1F6F63; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-bottom: 10px; }}
  .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #777; border-top: 1px solid #ddd; padding-top: 20px; }}
  @media print {{ body {{ padding: 0; }} .cover {{ padding: 100px 0; }} }}
</style>
</head>
<body>
  <div class="cover">
    <h1>{name}</h1>
    <p>پکیج اختصاصی Metatya — اثر آیت قمری</p>
  </div>
  <div class="content">
    {content}
  </div>
  <div class="footer">
    این محتوا آموزشی است و توصیه سرمایه‌گذاری نیست.<br>
    Metatya.ir
  </div>
</body>
</html>"""

for key, sec in data["sections"].items():
    name = sec["name"]
    items = sec["items"]
    
    html_content = ""
    for it in items:
        html_content += f"<span class='tag'>{E(it.get('tab', ''))}</span>"
        html_content += f"<h3>{E(it['title'])}</h3>"
        html_content += f"<p>{E(it['body'])}</p>"
        
    final_html = TPL.format(name=E(name), content=html_content)
    
    out_file = os.path.join(OUT_DIR, f"{key}-pack.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(final_html)
        
SB_URL = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or ""
if not (SB_URL and SB_KEY):
    print("هشدار: SUPABASE_URL یا SUPABASE_SERVICE_KEY تنظیم نیست؛ فایل‌ها فقط محلی ساخته شدند و ربات نمی‌تواند بفرستد.")
else:
    for name in os.listdir(OUT_DIR):
        if not name.endswith("-pack.html"):
            continue
        with open(os.path.join(OUT_DIR, name), "rb") as f:
            body = f.read()
        req = urllib.request.Request(
            f"{SB_URL}/storage/v1/object/paid-packs/packs/{name}", data=body, method="POST",
            headers={"Authorization": f"Bearer {SB_KEY}", "apikey": SB_KEY,
                     "Content-Type": "text/html; charset=utf-8", "x-upsert": "true"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print("آپلود شد (خصوصی):", name, r.status)
        except urllib.error.HTTPError as e:
            print("آپلود نشد:", name, e.code, e.read()[:200])
print("بسته‌های اختصاصی ساخته شدند.")
