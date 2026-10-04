"""ساخت صفحات ایستای SEO از docs/content.json: docs/p/*.html + sitemap.xml + robots.txt + feed.xml + latest.json
هر مطلب یک URL مستقل دارد (برای گوگل و اشتراک در تلگرام/اینستاگرام/یوتیوب) و به سایت/کانال‌ها لینک می‌دهد.
نیاز: SITE_URL (مثل https://user.github.io/metatya/)."""
import os, re, json, html, datetime, hashlib
ROOT = os.path.join(os.path.dirname(__file__), "..", "docs")
SITE = (os.environ.get("SITE_URL") or "").rstrip("/")
data = json.load(open(os.path.join(ROOT, "content.json"), encoding="utf-8"))
E = html.escape
def slug(key, it):
    h = hashlib.md5((it["title"] + it.get("date", "")).encode()).hexdigest()[:6]
    return f"{key}-{it.get('date','')}-{h}.html"
TPL = """<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} | Metatya</title>
<meta name="description" content="{desc}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:locale" content="fa_IR">
<meta name="twitter:card" content="summary"><link rel="manifest" href="../manifest.json"><meta name="theme-color" content="#1F6F63">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;800&display=swap" rel="stylesheet">
<script type="application/ld+json">{ld}</script>
<style>:root{{--bg:#EEF3F1;--card:#fff;--ink:#0F241F;--sub:#4C635D;--teal:#1F6F63;--gold:#C08A2E;--line:#DCE6E2}}@media(prefers-color-scheme:dark){{:root{{--bg:#0F1A17;--card:#152621;--ink:#EAF2EF;--sub:#9BB0AA;--line:#233631}}}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Vazirmatn',sans-serif;background:var(--bg);color:var(--ink);line-height:2}}.w{{max-width:640px;margin:0 auto;padding:18px 16px 60px}}
a.home{{color:var(--teal);font-size:13px;text-decoration:none}}.tag{{display:inline-block;font-size:11px;color:var(--gold);margin-top:14px}}h1{{font-size:21px;line-height:1.7;margin:4px 0 10px}}.meta{{font-size:11.5px;color:var(--sub)}}
article p{{font-size:14.5px;margin:12px 0}}.src a{{color:var(--teal);font-size:12px;margin-left:10px}}.warn{{font-size:11.5px;color:var(--sub);border-top:1px solid var(--line);margin-top:20px;padding-top:10px}}</style></head>
<body><div class="w"><a class="home" href="../index.html">← Metatya | همه‌ی حوزه‌ها</a>
<article><div class="tag">{name} · {tab}</div><h1>{title}</h1><div class="meta">{date}</div><p>{body}</p><div class="src">{src}</div>
<div class="warn">این محتوا آموزشی و اطلاع‌رسانی است و توصیه‌ی خرید، فروش، سرمایه‌گذاری، پزشکی یا حقوقی نیست؛ پیش از هر تصمیم، ریسک و شرایط خودتان را بسنجید.</div></article>
<div id="cta"></div><div style="text-align:center;margin-top:10px"><button class="mt-btn" id="sh" style="padding:9px 18px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);font-family:inherit">اشتراک‌گذاری</button></div></div>
<script src="../cta.js"></script><script>var c=document.getElementById('cta');MetatyaCTA.offers(c,'{key}','../');MetatyaCTA.lead(c,'article-{key}');MetatyaCTA.social(c,'article');MetatyaCTA.share(document.getElementById('sh'),{jt});</script></body></html>"""

os.makedirs(os.path.join(ROOT, "p"), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, "p")):
    if f.endswith(".html"): os.remove(os.path.join(ROOT, "p", f))
urls, latest, feed = [], {}, []
for key, sec in data["sections"].items():
    for i, it in enumerate(sec["items"]):
        fn = slug(key, it); rel = "p/" + fn; url = f"{SITE}/{rel}" if SITE else rel
        body = it["body"]; desc = E(re.sub(r"\s+", " ", body)[:155])
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": it["title"], "inLanguage": "fa",
                         "datePublished": it.get("date", ""), "articleSection": sec["name"], "description": re.sub(r"\s+", " ", body)[:155],
                         "author": {"@type": "Organization", "name": "Metatya"}, "mainEntityOfPage": url}, ensure_ascii=False).replace("</", "<\\/")
        src = "".join(f'<a href="{E(u)}" target="_blank" rel="noopener">منبع {n+1}</a>' for n, u in enumerate(it.get("sources", [])) if u.startswith("http"))
        open(os.path.join(ROOT, rel), "w", encoding="utf-8").write(TPL.format(
            title=E(it["title"]), desc=desc, url=E(url), ld=ld, name=E(sec["name"]), tab=E(it["tab"]), date=E(it.get("date", "")),
            body=E(body), src=src, key=key, jt=json.dumps(it["title"], ensure_ascii=False).replace("</", "<\\/")))
        urls.append((url, it.get("date", "")))
        if i == 0: latest[key] = rel
        if len(feed) < 40 and i == 0: feed.append((it, sec["name"], url))
now = datetime.datetime.now(datetime.timezone.utc)
home = (SITE + "/") if SITE else "index.html"
sm = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' \
     + f"<url><loc>{E(home)}</loc><lastmod>{now.date()}</lastmod></url>" \
     + "".join(f"<url><loc>{E(u)}</loc><lastmod>{d or now.date()}</lastmod></url>" for u, d in urls) + "</urlset>"
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n" + (f"Sitemap: {SITE}/sitemap.xml\n" if SITE else ""))
rss = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Metatya</title>' + f"<link>{E(home)}</link><description>تحلیل بازارها و یادگیری مالی</description><language>fa</language>" \
      + "".join(f"<item><title>{E(it['title'])}</title><link>{E(u)}</link><guid>{E(u)}</guid><description>{E(it['body'][:300])}</description><category>{E(n)}</category></item>" for it, n, u in feed) + "</channel></rss>"
open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8").write(rss)
json.dump(latest, open(os.path.join(ROOT, "latest.json"), "w"), ensure_ascii=False)
print(f"{len(urls)} صفحه مقاله ساخته شد + sitemap.xml + feed.xml")
