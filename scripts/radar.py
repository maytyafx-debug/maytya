"""ربات «جستجوگر فرصت» (اخلاقی): در منابع RSS عمومی دنبال گفت‌وگوهایی می‌گردد که مخاطب هدف درباره‌ی دردی می‌پرسد
که پک‌های Metatya برایش ابزار دارد، و فهرست خصوصی «فرصت‌های پاسخ مفید» می‌سازد.
قواعد: فقط محتوای عمومی؛ هیچ داده‌ی شخصی ذخیره نمی‌شود؛ هیچ پیام ناخواسته‌ای به کسی فرستاده نمی‌شود.
خروجی: خلاصه در چت خصوصی شما (TELEGRAM_REVIEW_CHAT_ID) یا چاپ در لاگ. تکراری‌ها در data/radar_seen.json می‌مانند."""
import os, json, re, hashlib
import xml.etree.ElementTree as ET
import requests

ROOT = os.path.join(os.path.dirname(__file__), "..")
CFG = json.load(open(os.path.join(ROOT, "config", "radar.json"), encoding="utf-8"))
SEEN_P = os.path.join(ROOT, "data", "radar_seen.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; MetatyaRadar/1.0; +public-rss)"}
ANGLE = {"risk": "درباره‌ی ثبت معاملات و حجم‌یاب رایگان", "biz": "درباره‌ی نقطه‌ی سربه‌سر و اعتبارسنجی مشتری", "fit": "درباره‌ی ثبت تمرین و عادت", "mind": "درباره‌ی ثبت فکر و خلق"}

def items(src):
    try:
        r = requests.get(src["url"], timeout=25, headers=UA); r.raise_for_status(); root = ET.fromstring(r.content); out = []
        for it in list(root.iter("item")) + list(root.iter("{http://www.w3.org/2005/Atom}entry")):
            t = (it.findtext("title") or it.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
            l = it.findtext("link") or ""
            if not l:
                e = it.find("{http://www.w3.org/2005/Atom}link"); l = e.get("href") if e is not None else ""
            if t and l: out.append((t, l.strip()))
        return out
    except Exception as e:
        print("  خطا:", src["name"], str(e)[:60]); return []

def score(title):
    tl = title.lower(); return sum(1 for k in CFG["keywords"] if k.lower() in tl)

def main():
    seen = set(json.load(open(SEEN_P, encoding="utf-8"))) if os.path.exists(SEEN_P) else set()
    found, run_seen = [], set()
    for src in CFG["sources"]:
        for t, l in items(src):
            h = hashlib.md5(l.encode()).hexdigest()[:12]
            if h in seen or h in run_seen: continue
            run_seen.add(h)
            s = score(t)
            if s: found.append((s, src, t, l, h))
    found.sort(key=lambda x: -x[0]); top = found[:8]
    if not top: print("فرصت تازه‌ای پیدا نشد"); return
    lines = ["🔭 فرصت‌های پاسخ مفید (فقط عمومی)\n"]
    for s, src, t, l, h in top:
        lines.append(f"• [{src['name']}] {t[:110]}\n  {l}\n  پیشنهاد: اگر واقعاً به سؤال کمک می‌کند، مفید جواب بده و {ANGLE.get(src['pack'], '')} را فقط در صورت ارتباط و بدون اسپم معرفی کن.\n")
    lines.append("⚠️ به غریبه‌ها پیام خصوصی ناخواسته نده؛ فقط در همان بحث عمومی و با رعایت قوانین همان سایت پاسخ بده.")
    text = "\n".join(lines)[:3900]; print(text)
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_REVIEW_CHAT_ID")
    if tok and chat:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", json={"chat_id": chat, "text": text, "disable_web_page_preview": True}, timeout=30)
        print("telegram:", r.status_code)
    seen.update(h for *_, h in top); os.makedirs(os.path.dirname(SEEN_P), exist_ok=True)
    json.dump(sorted(seen)[-2000:], open(SEEN_P, "w"), indent=0)

if __name__ == "__main__":
    main()
