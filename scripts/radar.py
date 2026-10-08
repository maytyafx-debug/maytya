"""جستجوگر فرصت‌های مشتری (قانونی و اخلاقی): منابع عمومی RSS را برای «سؤال/دردی که محصول ما جوابش است» می‌گردد
و فهرست امتیازدار + پیش‌نویس پاسخ مفید را فقط برای خود شما می‌فرستد (TELEGRAM_REVIEW_CHAT_ID).
هرگز به غریبه پیام نمی‌دهد، کانال یا گروهی را اسپم نمی‌کند و داده‌ی شخصی جمع نمی‌کند (فقط عنوان و لینک عمومی).
خروجی ماندگار: data/radar_seen.json (فقط لینک‌های دیده‌شده برای جلوگیری از تکرار)."""
import os, re, json, datetime
import xml.etree.ElementTree as ET
import requests
ROOT = os.path.join(os.path.dirname(__file__), "..")
CFG = json.load(open(os.path.join(ROOT, "config", "radar.json"), encoding="utf-8"))
SEEN_P = os.path.join(ROOT, "data", "radar_seen.json")
PACK = {"risk": "پک مدیریت ریسک", "fit": "پک تمرین", "mind": "پک ۲۱ روز ذهن آرام‌تر", "biz": "پک کسب‌وکار"}
QUESTION = re.compile(r"(\?|؟|چطور|چگونه|چرا|کمک|how |why |help|should i)", re.I)
UA = {"User-Agent": "Mozilla/5.0 MetatyaRadar"}

def score(title, kws):
    t = title.lower(); s = sum(2 for k in kws if k.lower() in t)
    return s + (1 if QUESTION.search(title) else 0)

def main():
    os.makedirs(os.path.dirname(SEEN_P), exist_ok=True)
    seen = set(json.load(open(SEEN_P, encoding="utf-8"))) if os.path.exists(SEEN_P) else set()
    found = []
    for q in CFG["queries"]:
        try:
            r = requests.get(q["url"], timeout=25, headers=UA); r.raise_for_status()
            for it in ET.fromstring(r.content).iter("item"):
                title = (it.findtext("title") or "").strip(); link = (it.findtext("link") or "").strip()
                if not title or not link or link in seen: continue
                sc = score(title, q["keywords"])
                if sc >= 2: found.append((sc, q, title, link))
        except Exception as e:
            print("  خطا:", q["label"], str(e)[:60])
    found.sort(key=lambda x: -x[0]); top = found[:8]
    for _, _, _, link in found: seen.add(link)
    json.dump(sorted(seen)[-2000:], open(SEEN_P, "w", encoding="utf-8"))
    print(f"فرصت جدید: {len(found)} (نمایش {len(top)})")
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_REVIEW_CHAT_ID")
    if not top or not (tok and chat): return
    lines = [f"🔎 فرصت‌های پاسخ مفید ({datetime.date.today()})\nفقط عمومی؛ خودت تصمیم بگیر که پاسخ بدهی یا نه. پاسخ کوتاه و کمک‌کننده بده، نه تبلیغ.\n"]
    for sc, q, title, link in top:
        lines.append(f"• [{q['label']}] {title}\n  {link}\n  اگر مرتبط بود: اول مشکلش را کمک کن، بعد (فقط اگر خواست) «{PACK.get(q['topic'], 'پک')}» را معرفی کن.")
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", json={"chat_id": chat, "text": "\n".join(lines)[:3900], "disable_web_page_preview": True}, timeout=30)

if __name__ == "__main__":
    main()
