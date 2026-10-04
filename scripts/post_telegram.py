"""ارسال خلاصه امروز به کانال تلگرام. نیاز: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SITE_URL"""
import os, json, requests
tok, chat = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
site = os.environ.get("SITE_URL", "")
latest = {}
try: latest = json.load(open(os.path.join(os.path.dirname(__file__), "..", "docs", "latest.json"), encoding="utf-8"))
except Exception: pass
data = json.load(open(os.path.join(os.path.dirname(__file__), "..", "docs", "content.json"), encoding="utf-8"))
for key in ("forex", "crypto", "bourse"):
    sec = data["sections"].get(key)
    if not sec or not sec["items"]:
        continue
    it = sec["items"][0]
    link = (site.rstrip("/") + "/" + latest[key] + "?utm_source=telegram&utm_medium=bot") if key in latest and site else site
    text = f"📌 {sec['name']} | {it['title']}\n\n{it['body']}\n\n⚠️ توصیه سرمایه‌گذاری نیست.\n🔗 {link}"
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", json={"chat_id": chat, "text": text}, timeout=30)
    print(key, r.status_code)
