"""تولید روزانه محتوای همه حوزه‌ها -> docs/content.json
ارائه‌دهنده: OpenRouter (رایگان، ۵۰ درخواست در روز، بدون محدودیت جغرافیایی).
بازارها: تیتر خبرهای روز از RSS رایگان؛ مدل فقط بر پایه همان‌ها می‌نویسد.
دروازه کیفیت: ساختار، زبان فارسی، طول، عبارت‌های ممنوع؛ هشدار ریسک همیشه با کد اضافه می‌شود."""
import os, sys, json, re, time, datetime
import xml.etree.ElementTree as ET
import requests
from sections import SECTIONS

DRY = "--dry" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "..", "out" if DRY else "docs", "dry-content.json" if DRY else "content.json")
KEEP = 40
DEAD, FAILS = set(), {}


def E(name, default=""):
    return (os.environ.get(name) or default).strip()


GN = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{lang}"
FEEDS = {
    "forex":  [GN.format(q="forex+EURUSD+dollar+gold+Fed", hl="en-US", gl="US", lang="en"), "https://www.fxstreet.com/rss/news"],
    "crypto": [GN.format(q="bitcoin+price+ETF", hl="en-US", gl="US", lang="en"), "https://cointelegraph.com/rss"],
    "bourse": [GN.format(q="%D8%B4%D8%A7%D8%AE%D8%B5+%DA%A9%D9%84+%D8%A8%D9%88%D8%B1%D8%B3+%D8%AA%D9%87%D8%B1%D8%A7%D9%86", hl="fa", gl="IR", lang="fa")],
}
DISCLAIMER = {
    "fin": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "med": "جایگزین مشاوره پزشک نیست.",
    "law": "اطلاعات عمومی است و جایگزین مشاوره وکیل نیست.",
}
KIND = {
    "forex": "fin", "crypto": "fin", "bourse": "fin",
    "income": "fin", "business": "fin", "finance": "fin",
    "sport": "med", "health": "med", "law": "law"
}
BANNED = ["سود تضمینی", "تضمین سود", "بدون ریسک", "قطعا سود", "قطعاً سود", "تضمینی"]

PROMPT = """امروز {today} است. برای بخش «{name}» یک سایت فارسی، برای هر یک از تب‌های {tabs} یک مطلب بنویس.
{ctx}قوانین: فارسی روان و دقیق؛ هر body بین ۴۰ تا ۹۰ کلمه؛ بدون وعده سود قطعی؛ عدد و خبر از خودت نساز؛ در سلامت و حقوق توصیه عمومی بده.
موضوع‌هایی که قبلاً نوشته شده و تکرار نکن: {old}
برای هر مطلب یک short_script هم بنویس: آرایه دقیقاً ۳ جمله خیلی کوتاه برای ویدیوی ۱۰ ثانیه‌ای. جمله‌ی اول هوک است: حداکثر ۸ کلمه، یک سؤال تیز یا یک تناقض/عدد جالب از همین مطلب (نه کلیشه مثل «آیا می‌دانستید»). جمله‌ی دوم یک نکته‌ی عملی، جمله‌ی سوم جمع‌بندی یا یک سؤال برای کامنت.
فقط JSON خالص برگردان: {{"items":[{{"tab":"...","title":"...","body":"...","short_script":["...","...","..."]}}]}}"""


# ---------- ارائه‌دهنده: OpenRouter ----------
def openrouter(prompt):
    key = E("OPENROUTER_API_KEY")
    model = E("OR_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
    url = "https://openrouter.ai/api/v1/chat/completions"
    body = {
        "model": model,
        "temperature": 0.4,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "You reply only with valid JSON. No markdown, no code fences."},
            {"role": "user", "content": prompt}
        ]
    }
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://maytyafx-debug.github.io/maytya/",
            "X-Title": "Metatya"
        },
        json=body,
        timeout=180
    )
    if r.status_code != 200:
        print(f"  OpenRouter raw error: {r.status_code} | {r.text[:300]}")
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def providers():
    p = []
    if E("OPENROUTER_API_KEY"):
        p.append(("openrouter", openrouter, 3))
    return p


# ---------- خبر و کیفیت ----------
def headlines(key):
    out = []
    for u in FEEDS.get(key, []):
        try:
            r = requests.get(u, timeout=20, headers={"User-Agent": "Mozilla/5.0 MetatyaBot"})
            for it in ET.fromstring(r.content).iter("item"):
                t = (it.findtext("title") or "").strip()
                if t: out.append(t)
                if len(out) >= 25: break
        except Exception as e:
            print("  RSS خطا:", u[:50], e)
    return out[:25]


def fa_ratio(t):
    letters = [c for c in t if c.isalpha()]
    return sum('\u0600' <= c <= '\u06ff' for c in letters) / len(letters) if letters else 0


def clean(items, tabs, key):
    good = []
    for it in items if isinstance(items, list) else []:
        try:
            t, b, ss = it["title"].strip(), it["body"].strip(), it["short_script"]
            ok = (it.get("tab") in tabs and 5 <= len(t) <= 140 and 60 <= len(b) <= 900
                  and fa_ratio(t + b) >= 0.6 and isinstance(ss, list) and len(ss) == 3
                  and all(isinstance(x, str) and 3 <= len(x) <= 120 for x in ss)
                  and not any(w in t + b for w in BANNED))
        except Exception:
            ok = False
        if ok:
            d = DISCLAIMER.get(KIND.get(key, ""), "")
            good.append({"tab": it["tab"], "title": t, "body": b + (" " + d if d and d not in b else ""), "short_script": ss})
    if not good: raise ValueError("هیچ مطلب سالمی از دروازه کیفیت رد نشد")
    return good


def ask(key, name, tabs, old_titles, provs):
    if DRY:
        return [{"tab": t, "title": f"نمونه {name} - {t}", "body": "متن نمونه (حالت آزمایشی).",
                 "short_script": ["هوک نمونه", "نکته نمونه", "جمع‌بندی نمونه"], "sources": []} for t in tabs], "dry"
    ctx, srcs = "", []
    if key in FEEDS:
        hl = headlines(key)
        ctx = ("تیتر خبرهای امروز (فقط بر اساس همین‌ها بنویس؛ اگر عدد دقیق نیست بنویس عدد را از منبع ببین):\n- " + "\n- ".join(hl) + "\n") if hl \
              else "خبر امروز در دسترس نیست؛ فقط آموزش و مفهوم بنویس و قیمت یا خبری نساز.\n"
        srcs = [u for u in FEEDS[key] if "news.google" not in u]
    prompt = PROMPT.format(today=datetime.date.today().isoformat(), name=name, tabs="، ".join(tabs), ctx=ctx,
                           old="، ".join(old_titles[:12]) or "ندارد")
    err = []
    for pname, fn, _ in provs:
        if pname in DEAD: continue
        for attempt in range(3):
            try:
                txt = fn(prompt)
                items = clean(json.loads(re.search(r"\{.*\}", txt, re.S).group(0))["items"], tabs, key)
                for it in items: it["sources"] = srcs
                return items, pname
            except requests.HTTPError as e:
                err.append(f"{pname}:{e.response.status_code}")
                if e.response.status_code in (401, 403):
                    DEAD.add(pname)
                    print(f"  {pname} کلید نامعتبر — کنار گذاشته شد")
                    break
                if e.response.status_code == 429:
                    wait = 30 * (attempt + 1)
                    print(f"  {pname} سهمیه — صبر {wait}s")
                    time.sleep(wait)
                    continue
                time.sleep(2)
            except Exception as e:
                err.append(f"{pname}:{str(e)[:60]}")
                time.sleep(2)
    raise RuntimeError("OpenRouter شکست خورد: " + " | ".join(err))


def main():
    provs = providers()
    if not DRY and not provs:
        sys.exit("OPENROUTER_API_KEY تنظیم نشده")
    pause = min((p[2] for p in provs), default=0)
    old = {}
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8")).get("sections", {})
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    result, first, used = {}, True, {}
    for key, (name, tabs, _) in SECTIONS.items():
        prev = old.get(key, {}).get("items", [])
        try:
            if not DRY and not first: time.sleep(pause)
            first = False
            items, who = ask(key, name, tabs, [p["title"] for p in prev], provs)
            for it in items: it["date"] = now[:10]
            result[key] = {"name": name, "items": (items + prev)[:KEEP], "ok": True, "provider": who}
            used[who] = used.get(who, 0) + 1
            print("OK  ", key, len(items), who)
        except Exception as e:
            print("FAIL", key, e)
            result[key] = {"name": name, "items": prev, "ok": False, "error": str(e)[:200]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    note = "خلاصه‌ی تیتر خبرهای عمومی؛ قیمت‌ها لحظه‌ای نیستند. مطالب مالی، سلامت و حقوق جایگزین مشاوره متخصص نیستند."
    json.dump({"updated": now, "note": note, "sections": result}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = sum(1 for v in result.values() if v["ok"])
    print(f"گزارش: {ok}/{len(result)} حوزه به‌روز شد | ارائه‌دهنده‌ها: {used}")
    if ok == 0: sys.exit(1)


if __name__ == "__main__":
    main()
