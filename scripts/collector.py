"""ربات جمع‌آوری داده (بانک اطلاعاتی روزانه) -> docs/data/latest.json + docs/data/history/YYYY-MM-DD.json
قیمت‌ها از API رایگان (CoinGecko، Frankfurter/ECB) و تیتر خبرها از RSS عمومی.
اختیاری: اگر SUPABASE_URL و SUPABASE_SERVICE_KEY تنظیم باشد، همان داده در جدول data_bank هم ذخیره می‌شود.
هیچ داده‌ی شخصی جمع نمی‌شود."""
import os, json, datetime, time
import xml.etree.ElementTree as ET
import requests

ROOT = os.environ.get("DATA_DIR") or os.path.join(os.path.dirname(__file__), "..", "docs", "data")
UA = {"User-Agent": "Mozilla/5.0 MetatyaBot"}
GN = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{lang}"
def gn(q, fa=False):
    return GN.format(q=q, hl="fa" if fa else "en-US", gl="IR" if fa else "US", lang="fa" if fa else "en")
NEWS = {
    "forex": [gn("forex+dollar+euro+gold+Fed")], "crypto": [gn("bitcoin+ethereum+crypto+ETF")],
    "bourse": [gn("%D8%B4%D8%A7%D8%AE%D8%B5+%DA%A9%D9%84+%D8%A8%D9%88%D8%B1%D8%B3+%D8%AA%D9%87%D8%B1%D8%A7%D9%86", True)],
    "sport": [gn("%D8%AA%D9%85%D8%B1%DB%8C%D9%86+%D8%A8%D8%AF%D9%86%D8%B3%D8%A7%D8%B2%DB%8C+%D8%AA%D8%BA%D8%B0%DB%8C%D9%87+%D9%88%D8%B1%D8%B2%D8%B4%DB%8C", True), gn("strength+training+nutrition+research")],
    "psychology": [gn("%D8%B1%D9%88%D8%A7%D9%86%D8%B4%D9%86%D8%A7%D8%B3%DB%8C+%D8%B3%D9%84%D8%A7%D9%85%D8%AA+%D8%B1%D9%88%D8%A7%D9%86", True), gn("psychology+mental+health+study")],
    "business": [gn("%DA%A9%D8%B3%D8%A8+%D9%88+%DA%A9%D8%A7%D8%B1+%D8%A7%D8%B3%D8%AA%D8%A7%D8%B1%D8%AA%D8%A7%D9%BE+%DA%A9%D8%B3%D8%A8%E2%80%8C%D9%88%DA%A9%D8%A7%D8%B1", True), gn("small+business+startup+trends")],
    "health": [gn("%D8%B3%D9%84%D8%A7%D9%85%D8%AA+%D8%AA%D8%BA%D8%B0%DB%8C%D9%87+%D8%AE%D9%88%D8%A7%D8%A8", True)],
}

def jget(url):
    try:
        r = requests.get(url, timeout=25, headers=UA); r.raise_for_status(); return r.json()
    except Exception as e:
        print("  خطا:", url[:60], str(e)[:60]); return None

def prices():
    out = {}
    c = jget("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple&vs_currencies=usd&include_24hr_change=true")
    for k, sym in (("bitcoin", "BTC"), ("ethereum", "ETH"), ("solana", "SOL"), ("ripple", "XRP")):
        if c and k in c and isinstance(c[k].get("usd"), (int, float)):
            out[f"{sym}/USD"] = {"value": c[k]["usd"], "change24h_pct": round(c[k].get("usd_24h_change") or 0, 2), "source": "CoinGecko"}
    f = jget("https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,GBP,JPY,CHF,CAD,AUD")
    if f and f.get("rates"):
        r = f["rates"]
        for sym, inv in (("EUR/USD", "EUR"), ("GBP/USD", "GBP"), ("AUD/USD", "AUD")):
            if inv in r and r[inv]: out[sym] = {"value": round(1 / r[inv], 5), "date": f.get("date"), "source": "ECB/Frankfurter"}
        for sym, q in (("USD/JPY", "JPY"), ("USD/CHF", "CHF"), ("USD/CAD", "CAD")):
            if q in r: out[sym] = {"value": r[q], "date": f.get("date"), "source": "ECB/Frankfurter"}
    return out

def headlines(urls, n=8):
    seen, items = set(), []
    for u in urls:
        try:
            r = requests.get(u, timeout=25, headers=UA); r.raise_for_status()
            for it in ET.fromstring(r.content).iter("item"):
                t = (it.findtext("title") or "").strip()
                if t and t not in seen:
                    seen.add(t); items.append({"title": t, "link": (it.findtext("link") or "").strip(), "published": (it.findtext("pubDate") or "").strip()})
        except Exception as e:
            print("  RSS خطا:", u[:50], str(e)[:50])
    return items[:n]

def push_supabase(rows):
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not (url and key): return "غیرفعال (کلید تنظیم نشده)"
    try:
        r = requests.post(url.rstrip("/") + "/rest/v1/data_bank", json=rows, timeout=30,
                          headers={"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json", "Prefer": "return=minimal"})
        return f"HTTP {r.status_code}" + ("" if r.ok else " " + r.text[:100])
    except Exception as e:
        return "خطا: " + str(e)[:80]

def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    snap = {"updated": now.isoformat(timespec="seconds"), "prices": prices(), "news": {}}
    for k, urls in NEWS.items():
        snap["news"][k] = headlines(urls); time.sleep(0.5)
    os.makedirs(os.path.join(ROOT, "history"), exist_ok=True)
    json.dump(snap, open(os.path.join(ROOT, "latest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(snap, open(os.path.join(ROOT, "history", now.date().isoformat() + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    for f in sorted(os.listdir(os.path.join(ROOT, "history")))[:-60]:
        os.remove(os.path.join(ROOT, "history", f))
    rows = [{"kind": "price", "key": k, "payload": v} for k, v in snap["prices"].items()] + \
           [{"kind": "news", "key": k, "payload": {"items": v}} for k, v in snap["news"].items() if v]
    n_news = sum(len(v) for v in snap["news"].values())
    print(f"بانک داده: {len(snap['prices'])} قیمت، {n_news} تیتر در {sum(1 for v in snap['news'].values() if v)} حوزه | Supabase: {push_supabase(rows) if rows else 'داده‌ای نبود'}")
    if not snap["prices"] and not n_news: raise SystemExit(1)

if __name__ == "__main__":
    main()
