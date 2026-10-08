"""ارسال خلاصه امروز به کانال تلگرام. نیاز: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SITE_URL"""
import os, json, requests, datetime
import html as _h
EMO = {"forex": "💱", "crypto": "🪙", "bourse": "📈"}
CTA = ["متن کامل و منبع‌ها", "ادامه‌ی ماجرا", "همه‌ی جزئیات اینجاست", "برای خواندن کامل"]
ASK = ["تو چطور فکر می‌کنی؟ 👇", "نظرت چیست؟ 👇", "تجربه‌ی خودت را بنویس 👇", "با این موافقی؟ 👇"]
FIN = ("forex", "crypto", "bourse")
def build_post(key, sec, it, link):
    """پست صمیمی و متنوع: عنوان کوتاه + متن tg (تولیدشده با لحن دوستانه) + لینک پنهان پشت متن. اگر tg نبود، از متن اصلی پیش‌نویس ساده می‌سازد."""
    e = _h.escape; n = datetime.date.today().toordinal() + sum(map(ord, key))
    tg = it.get("tg")
    if not tg:
        sents = [x.strip() for x in it["body"].replace("؟", "؟.").split(".") if x.strip()][:2]
        tg = ". ".join(sents).strip() + ". " + ASK[n % len(ASK)]
    out = [f"{EMO.get(key, '📌')} <b>{e(it['title'])}</b>", "", e(tg), "", f'👉 <a href="{e(link)}">{CTA[n % len(CTA)]}</a>']
    if key in FIN: out += ["", "<i>آموزشی است؛ توصیه‌ی سرمایه‌گذاری نیست.</i>"]
    return "\n".join(out)
tok, chat = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
# POST_MODE=review: پست‌ها فقط به چت خصوصی خودتان با ربات می‌روند (بدون سرور و رایگان)؛ اگر خوب بود دستی فوروارد کنید.
# POST_MODE=auto (پیش‌فرض): مستقیم در کانال منتشر می‌شود.
MODE = os.environ.get("POST_MODE", "auto")
if MODE == "review":
    chat = os.environ.get("TELEGRAM_REVIEW_CHAT_ID", "")
    if not chat: raise SystemExit("POST_MODE=review ولی TELEGRAM_REVIEW_CHAT_ID تنظیم نشده؛ چیزی ارسال نشد")
site = os.environ.get("SITE_URL", "")
latest = {}
try: latest = json.load(open(os.path.join(os.path.dirname(__file__), "..", "docs", "latest.json"), encoding="utf-8"))
except Exception: pass
data = json.load(open(os.path.join(os.path.dirname(__file__), "..", "docs", "content.json"), encoding="utf-8"))
POSTED = os.path.join(os.path.dirname(__file__), "..", "docs", "posted.json")
try: posted = json.load(open(POSTED, encoding="utf-8"))
except Exception: posted = {}
force = os.environ.get("FORCE_POST") == "1"
KEYS = [k.strip() for k in (os.environ.get("POST_KEYS") or "forex,crypto,bourse").split(",") if k.strip()]  # مثلاً POST_KEYS=forex تا فقط یک پست در روز برود
for key in KEYS:
    sec = data["sections"].get(key)
    if not sec or not sec["items"]:
        continue
    it = sec["items"][0]
    if it["title"].startswith("نمونه") or "حالت آزمایشی" in it["body"]:
        print(key, "محتوای نمونه است؛ ارسال نشد"); continue
    try: age = (datetime.date.today() - datetime.date.fromisoformat(it.get("date", "1970-01-01"))).days
    except Exception: age = 999
    if age > 3 and not force:
        print(key, f"محتوا {age} روز کهنه است؛ ارسال نشد"); continue
    sig = it["title"] + it.get("date", "")
    if posted.get(key) == sig and not force:
        print(key, "قبلاً ارسال شده؛ رد شد"); continue
    link = (site.rstrip("/") + "/" + latest[key] + "?ref=t") if key in latest and site else site   # آدرس کوتاه؛ ref=t فقط برای ثبت مبدأ (تلگرام)
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", json={"chat_id": chat, "text": build_post(key, sec, it, link), "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=30)
    print(key, r.status_code, "" if r.status_code == 200 else r.text[:200])
    if r.status_code == 200:
        if MODE != "review": posted[key] = sig
        vid = os.path.join(os.path.dirname(__file__), "..", "out", f"{key}_short.mp4")
        if os.environ.get("SEND_VIDEO") == "1" and os.path.exists(vid):   # پیش‌فرض: خاموش (فایل زیر هر پست حس اسپم می‌دهد)
            with open(vid, "rb") as fh:
                v = requests.post(f"https://api.telegram.org/bot{tok}/sendVideo", data={"chat_id": chat, "caption": f"🎬 {it['title']}"[:1000], "supports_streaming": "true"}, files={"video": fh}, timeout=120)
            print(key, "video", v.status_code, "" if v.status_code == 200 else v.text[:200])
json.dump(posted, open(POSTED, "w", encoding="utf-8"), ensure_ascii=False)
