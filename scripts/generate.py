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
    "forex":  [GN.format(q="forex+EURUSD+dollar+gold+Fed", hl="en-US", gl="US", lang="en"), ],
    "crypto": [GN.format(q="bitcoin+price+ETF", hl="en-US", gl="US", lang="en"), "https://cointelegraph.com/rss"],
    "bourse": [GN.format(q="%D8%B4%D8%A7%D8%AE%D8%B5+%DA%A9%D9%84+%D8%A8%D9%88%D8%B1%D8%B3+%D8%AA%D9%87%D8%B1%D8%A7%D9%86", hl="fa", gl="IR", lang="fa")],
}
DISCLAIMER = {
    "fin": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
    "med": "جایگزین مشاوره پزشک نیست.",
    "law": "اطلاعات عمومی است و جایگزین مشاوره وکیل نیست.",
    "general": "این محتوا آموزشی و عمومی است؛ برای تصمیم‌های حساس، اطلاعات را از منابع معتبر بررسی کن.",
}
KIND = {
    "forex": "fin", "crypto": "fin", "bourse": "fin",
    "income": "fin", "business": "fin", "finance": "fin",
    "sport": "med", "health": "med", "law": "law",
    "ai": "general", "privacy": "general"
}
BANNED = ["سود تضمینی", "تضمین سود", "بدون ریسک", "قطعا سود", "قطعاً سود", "تضمینی"]

PROMPT = """نقش تو: سردبیر ارشد و استراتژیست محتوای آموزشی پلتفرم فارسی Metatya هستی.

مشخصات:
تاریخ: {today}
حوزه: {name}
تب‌های مجاز: {tabs}
اطلاعات و زمینه خبری: {ctx}
عنوان‌های قبلی که نباید تکرار شوند: {old}

ماموریت:
برای تک‌تک تب‌های مجاز دقیقاً یک مطلب مستقل و ارزشمند تولید کن. هیچ تبی را حذف نکن و برای هیچ تبی چند مطلب نساز. موضوع هر مطلب باید با حوزه و تب مربوط کاملاً منطبق باشد.

استاندارد سردبیری:
۱. برای هر مطلب یک موضوع مشخص، مفید و غیرتکراری انتخاب کن.
۲. عنوان جذاب، روشن و دقیق باشد؛ بدون اغراق و وعده نتیجه.
۳. فارسی روان، طبیعی و حرفه‌ای بنویس.
۴. بدنه هر مطلب حدود ۶۰ تا ۹۰ واژه فارسی و بین ۶۰ تا ۹۰۰ نویسه باشد.
۵. هر مطلب باید یک مسئله را توضیح دهد، دلیل یا منطق آن را روشن کند و حداقل یک نکته آموزشی کاربردی داشته باشد.
۶. از مقدمه‌های طولانی، شعار، تکرار و جملات پرکننده پرهیز کن.
۷. مطالب قبلی را بازنویسی سطحی نکن؛ زاویه و ارزش آموزشی تازه ارائه بده.
۸. هیچ آمار، خبر، قیمت، نقل‌قول، قانون یا منبعی را جعل نکن.
۹. اگر اطلاعات خبری کافی نیست، به‌جای حدس‌زدن محتوای آموزشی ماندگار تولید کن.
۱۰. تیتر خبری به‌تنهایی اثبات‌کننده جزئیات یک رویداد نیست.

استاندارد حوزه‌ها:
- فارکس، کریپتو و بورس: آموزش مفاهیم، سازوکار بازار، سواد مالی و مدیریت ریسک. بدون سیگنال، نقطه ورود و خروج، پیش‌بینی قطعی یا توصیه سرمایه‌گذاری شخصی.
- کسب درآمد و کسب‌وکار: ایده‌های واقع‌بینانه همراه با مهارت موردنیاز، هزینه، زمان و ریسک؛ بدون تضمین درآمد.
- مالی شخصی: بودجه‌بندی، پس‌انداز، شناخت هزینه‌ها و تصمیم‌گیری آگاهانه.
- ورزش: آموزش عمومی و ایمن؛ بدون تمرین افراطی، توصیه مکمل یا ادعای درمان.
- روان‌شناسی: آموزش عمومی و غیرتشخیصی؛ بدون برچسب‌گذاری یا وعده درمان.
- سلامت: اطلاعات عمومی و محتاطانه؛ بدون تشخیص یا تجویز.
- حقوق: اطلاعات عمومی؛ بدون جعل ماده قانونی یا تضمین نتیجه پرونده. قوانین ممکن است بر اساس کشور و زمان تغییر کنند.
- تحصیل و پژوهش: مهارت یادگیری، روش تحقیق و تفکر نقادانه؛ بدون جعل منبع علمی.
- هوش مصنوعی: آموزش ابزارها، کاربردها، محدودیت‌ها، بررسی خروجی و اخلاق استفاده؛ بدون ادعای قطعی درباره توانایی ابزارها.
- امنیت و حریم خصوصی: حفاظت حساب‌ها، شناخت کلاهبرداری، حریم داده و امنیت دیجیتال؛ بدون درخواست یا انتشار رمز و اطلاعات محرمانه.

سناریوی ویدیویی:
برای هر مطلب فیلد short_script دقیقاً شامل سه جمله باشد:
۱. هوک جذاب و مرتبط، حداکثر ۸ واژه.
۲. یک نکته آموزشی یا کاربردی.
۳. جمع‌بندی یا پرسش مرتبط برای مشارکت مخاطب.
هر سه جمله باید با متن اصلی هماهنگ باشند و ادعای تازه‌ای اضافه نکنند.

قواعد خروجی:
- مقدار tab باید دقیقاً یکی از نام‌های تب‌های مجاز باشد.
- برای هر تب دقیقاً یک مطلب تولید کن.
- title و body رشته فارسی باشند.
- short_script دقیقاً سه رشته داشته باشد.
- فقط JSON معتبر برگردان؛ بدون Markdown و توضیح اضافه.
- ساختار دقیق خروجی:

{{"items":[{{"tab":"نام دقیق تب","title":"عنوان مطلب","body":"متن کامل مطلب","short_script":["هوک","نکته آموزشی","جمع‌بندی یا پرسش"]}}]}}"""


# ---------- ارائه‌دهنده: OpenRouter (با جایگزینی خودکار مدل) ----------
# لیست مدل‌های رایگان به ترتیب اولویت. اگر یکی خطا داد یا پولی/ناموجود شد، مدل بعدی امتحان می‌شود.
# می‌توانی با متغیر OR_MODELS (جداشده با ویرگول) این لیست را از بیرون عوض کنی.
OR_MODELS_DEFAULT = "nvidia/nemotron-3.5-super-vl:free,recursive/flint-v1.0:free,xingchen-agi/xing4.0-29b-a4b:free"


def or_models():
    return [m.strip() for m in E("OR_MODELS", OR_MODELS_DEFAULT).split(",") if m.strip()]


def openrouter(prompt):
    key = E("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    last = ""
    for model in or_models():
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
        try:
            r = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://maytyafx-debug.github.io/maytya/",
                    "X-Title": "Metatya"
                },
                json=body,
                timeout=60
            )
        except requests.RequestException as e:
            last = f"{model}:{str(e)[:60]}"
            print(f"  {model} ارتباط ناموفق — مدل بعدی")
            continue
        if r.status_code in (401, 403):
            # مشکل از کلید است؛ با تغییر مدل حل نمی‌شود
            r.raise_for_status()
        if r.status_code != 200:
            last = f"{model}:{r.status_code}"
            print(f"  {model} خطای {r.status_code} — مدل بعدی | {r.text[:120]}")
            continue
        content = r.json()["choices"][0]["message"].get("content") or ""
        if not content.strip():
            last = f"{model}:empty"
            print(f"  {model} پاسخ خالی — مدل بعدی")
            continue
        return content
    raise RuntimeError(f"همه مدل‌های رایگان شکست خوردند ({last})")


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
    good, why = [], {}
    for it in items if isinstance(items, list) else []:
        reason = None
        try:
            t, b, ss = it["title"].strip(), it["body"].strip(), it["short_script"]
            raw_tab = str(it.get("tab", "")).strip()

            def norm_tab(value):
                value = str(value).strip()
                value = value.replace("ي", "ی").replace("ك", "ک")
                value = re.sub(r"[\s‌ـ]+", "", value)
                return value

            tab_lookup = {norm_tab(t): t for t in tabs}
            tab = tab_lookup.get(norm_tab(raw_tab))

            if tab is None: reason = f"تب نامعتبر: {raw_tab[:40]}"
            elif not (5 <= len(t) <= 140): reason = "طول عنوان"
            elif not (60 <= len(b) <= 900): reason = "طول متن"
            elif fa_ratio(t + b) < 0.6: reason = "نسبت فارسی کم"
            elif not (isinstance(ss, list) and len(ss) == 3 and all(isinstance(x, str) and 3 <= len(x) <= 120 for x in ss)): reason = "خلاصه‌ی صوتی"
            elif any(w in t + b for w in BANNED): reason = "عبارت ممنوع"
        except Exception:
            reason = "ساختار JSON"
        if reason is None:
            d = DISCLAIMER.get(KIND.get(key, ""), "")
            good.append({"tab": tab, "title": t, "body": b + (" " + d if d and d not in b else ""), "short_script": ss})
        else:
            why[reason] = why.get(reason, 0) + 1
    counts = {tab: 0 for tab in tabs}

    for item in good:
        counts[item["tab"]] += 1

    missing = [tab for tab, count in counts.items() if count == 0]
    duplicated = [tab for tab, count in counts.items() if count > 1]

    if missing or duplicated:
        raise ValueError(
            f"پوشش تب‌ها ناقص است؛ "
            f"تب‌های جاافتاده: {missing}؛ "
            f"تب‌های تکراری: {duplicated}"
        )

    if why: print(f"  دروازه کیفیت [{key}] رد شد:", why)
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
        srcs = []
    prompt = PROMPT.format(today=datetime.date.today().isoformat(), name=name, tabs="، ".join(tabs), ctx=ctx,
                           old="، ".join(old_titles[:12]) or "ندارد")
    err = []
    for pname, fn, _ in provs:
        if pname in DEAD: continue
        for attempt in range(2):
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
