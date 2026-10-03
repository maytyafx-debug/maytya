"""تولید روزانه محتوای همه حوزه‌ها -> site/content.json
نیاز: ANTHROPIC_API_KEY. اجرا: python scripts/generate.py [--dry]"""
import os, sys, json, datetime, re
from sections import SECTIONS

DRY = "--dry" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "content.json")
MODEL = os.environ.get("MODEL", "claude-sonnet-4-6")
KEEP = 40

PROMPT = """امروز {today} است. برای بخش «{name}» یک سایت فارسی، برای هر یک از تب‌های {tabs} یک مطلب تازه و کاربردی بنویس.
{search}قوانین: فارسی روان؛ هر body حداکثر ۹۰ کلمه؛ بدون وعده سود قطعی؛ در بخش‌های مالی/بازار یادآوری ریسک؛ در سلامت و حقوق توصیه عمومی بده و ارجاع به متخصص.
برای هر مطلب یک short_script هم بنویس: آرایه ۳ جمله خیلی کوتاه (هوک، نکته، جمع‌بندی) برای ویدیوی ۱۰ ثانیه‌ای.
فقط JSON خالص برگردان، بدون بک‌تیک:
{{"items":[{{"tab":"...","title":"...","body":"...","short_script":["...","...","..."]}}]}}"""

def ask(key, name, tabs, web):
    if DRY:
        return [{"tab": t, "title": f"نمونه {name} - {t}", "body": "متن نمونه (حالت آزمایشی).",
                 "short_script": ["هوک نمونه", "نکته نمونه", "جمع‌بندی نمونه"]} for t in tabs]
    import anthropic
    c = anthropic.Anthropic()
    kw = {}
    if web:
        kw["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
    p = PROMPT.format(today=datetime.date.today().isoformat(), name=name, tabs="، ".join(tabs),
                      search="ابتدا با جستجوی وب جدیدترین اخبار و داده‌های همین هفته را بررسی کن. " if web else "")
    r = c.messages.create(model=MODEL, max_tokens=3000, messages=[{"role": "user", "content": p}], **kw)
    txt = "".join(b.text for b in r.content if b.type == "text")
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group(0))["items"]

def main():
    old = {}
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8")).get("sections", {})
    now = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    result = {}
    for key, (name, tabs, web) in SECTIONS.items():
        try:
            items = ask(key, name, tabs, web)
            for it in items:
                it["date"] = now[:10]
            prev = old.get(key, {}).get("items", [])
            result[key] = {"name": name, "items": (items + prev)[:KEEP], "ok": True}
            print("OK  ", key, len(items))
        except Exception as e:
            print("FAIL", key, e)
            result[key] = {"name": name, "items": old.get(key, {}).get("items", []), "ok": False, "error": str(e)[:200]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"updated": now, "sections": result}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = sum(1 for v in result.values() if v["ok"])
    print(f"گزارش: {ok}/{len(result)} حوزه با موفقیت به‌روز شد")

if __name__ == "__main__":
    main()
