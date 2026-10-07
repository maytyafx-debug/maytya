"""ثبت webhook هر ربات تلگرام روی Worker. نیاز: WORKER_URL, WEBHOOK_SECRET و توکن‌های BOT_RISK/BOT_BOURSE/BOT_FIT/BOT_MIND/BOT_BIZ (هرکدام که دارید)."""
import os, sys, requests
url = (os.environ.get("WORKER_URL") or "").rstrip("/")
if not url: sys.exit("WORKER_URL خالی است")
ok = 0
for key in ("risk", "bourse", "fit", "mind", "biz"):
    tok = os.environ.get("BOT_" + key.upper())
    if not tok: print(key, "— توکن ندارد؛ رد شد"); continue
    r = requests.post(f"https://api.telegram.org/bot{tok}/setWebhook", json={"url": f"{url}/tg/{key}", "secret_token": os.environ.get("WEBHOOK_SECRET", ""), "allowed_updates": ["message", "callback_query"], "drop_pending_updates": True}, timeout=30)
    print(key, r.status_code, r.json().get("description", "")); ok += r.ok
print(f"{ok} ربات فعال شد")
if ok == 0: sys.exit(1)
