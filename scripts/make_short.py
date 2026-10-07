"""ساخت ویدیوی عمودی ۱۰۸۰x۱۹۲۰ (~۱۲ تا ۱۸ ثانیه) با موشن‌گرافی، تایپوگرافی متحرک، صدای گوینده‌ی فارسی (edge-tts رایگان)،
موسیقی پس‌زمینه و افکت صوتی ساخته‌شده با ffmpeg (بدون مشکل کپی‌رایت) -> out/*_short.mp4 + *_cover.png + *_upload.txt
اگر TTS در دسترس نباشد، ویدیو بدون گوینده (فقط موسیقی و افکت) ساخته می‌شود.
آزمایش: python scripts/make_short.py --selftest | --demo
رندر فارسی: اگر Pillow با RAQM (حرف‌چین و راست‌به‌چپ داخلی) در دسترس باشد از همان استفاده می‌شود؛
وگرنه arabic-reshaper + python-bidi. فونت: FONT_PATH یا دانلود Vazirmatn یا فونت‌های سیستمی دارای حروف فارسی.
اجرای آزمایش: python scripts/make_short.py --selftest"""
import os, sys, json, subprocess, textwrap, urllib.request, shutil, asyncio, math, random, re, time
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features

ROOT = os.path.join(os.path.dirname(__file__), "..")
W, H = 1080, 1920
RAQM = features.check("raqm")
FONT_URLS = [
    "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/Vazirmatn-Regular.ttf",
    "https://cdn.jsdelivr.net/npm/vazirmatn@33.0.3/fonts/ttf/Vazirmatn-Regular.ttf",
]
SYSTEM_FALLBACKS = ["Vazirmatn", "Noto Sans Arabic", "Noto Naskh Arabic", "DejaVu Sans"]

def _ok_font(path):
    try:
        ImageFont.truetype(path, 40); return os.path.getsize(path) > 50_000
    except Exception:
        return False

def find_font():
    for p in (os.environ.get("FONT_PATH"), os.path.join(ROOT, "assets", "fonts", "Vazirmatn-Regular.ttf")):
        if p and os.path.exists(p) and _ok_font(p): return p
    dst = os.path.join(ROOT, "out", "Vazirmatn-Regular.ttf")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if _ok_font(dst): return dst
    for u in FONT_URLS:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(dst, "wb") as f: shutil.copyfileobj(r, f)
            if _ok_font(dst): print("فونت دانلود شد:", u); return dst
        except Exception as e:
            print("دانلود فونت ناموفق:", u[:60], e)
    for fam in SYSTEM_FALLBACKS:
        try:
            out = subprocess.run(["fc-match", "-f", "%{file}", fam + ":lang=fa"], capture_output=True, text=True).stdout.strip()
            if out and _ok_font(out): print("فونت سیستمی:", out); return out
        except Exception: pass
    sys.exit("هیچ فونت فارسی پیدا نشد؛ FONT_PATH را تنظیم کنید")

FONT = find_font()

if not RAQM:
    import arabic_reshaper
    try: from bidi import get_display            # python-bidi >= 0.5
    except ImportError: from bidi.algorithm import get_display
    _R = arabic_reshaper.ArabicReshaper(configuration={"delete_harakat": True})
    def prep(s): return get_display(_R.reshape(s))
else:
    def prep(s): return s                            # RAQM خودش حرف‌چینی و جهت را انجام می‌دهد

def font_at(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM if RAQM else ImageFont.Layout.BASIC)


FPS = 30
GOLD, INK = (255, 200, 87), (238, 243, 241)
NAMES = {"forex": "فارکس", "crypto": "کریپتو", "bourse": "بورس ایران"}
KW = {"direction": "rtl", "language": "fa"} if RAQM else {}
VOICE = os.environ.get("VOICE", "fa-IR-DilaraNeural")

def fl(size): return font_at(size)
def text_w(txt, fnt):
    return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(prep(txt), font=fnt, **KW)

def word_sprite(word, fnt, fill):
    d0 = ImageDraw.Draw(Image.new("L", (1, 1))); t = prep(word)
    l, tp, r, b = d0.textbbox((0, 0), t, font=fnt, **KW); w, h, pad = r - l, b - tp, 14
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((pad - l + 3, pad - tp + 5), t, font=fnt, fill=(0, 0, 0, 120), **KW)
    d.text((pad - l, pad - tp), t, font=fnt, fill=fill, **KW)
    return im, w, pad

def layout(text, size, yc, maxw=W - 150):
    fnt = fl(size); words = text.split(); sp = size * 0.3
    lines, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and text_w(trial, fnt) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur)
    hi = next((i for i, w in enumerate(words) if re.search(r"[0-9۰-۹]", w)), max(range(len(words)), key=lambda i: len(words[i])))
    lh = int(size * 1.6); y0 = yc - len(lines) * lh // 2; out, idx = [], 0
    for li, ln in enumerate(lines):
        ws = [text_w(w, fnt) for w in ln]; total = sum(ws) + sp * (len(ln) - 1); xr = W / 2 + total / 2
        for w, wd in zip(ln, ws):
            spr, ww, pad = word_sprite(w, fnt, GOLD if idx == hi else INK)
            out.append({"spr": spr, "x": int(xr - wd - pad), "y": y0 + li * lh - pad, "i": idx}); xr -= wd + sp; idx += 1
    return out, len(lines) * lh

def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c1, c3 = 1.4, 2.4; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def gradient(c1, c2):
    col = Image.new("RGB", (1, H))
    for y in range(H):
        k = y / (H - 1); col.putpixel((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3)))
    return col.resize((W, H))

def glow(size, color, alpha):
    m = Image.new("L", (size, size), 0); pad = size // 5
    ImageDraw.Draw(m).ellipse([pad, pad, size - pad, size - pad], fill=int(255 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(size / 6))
    g = Image.new("RGBA", (size, size), color + (0,)); g.putalpha(m); return g

def make_assets():
    A = {"bg1": gradient((8, 24, 21), (26, 96, 86)), "bg2": gradient((16, 30, 36), (43, 84, 96))}
    grid = Image.new("RGBA", (W, H + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(grid)
    for y in range(0, H + 120, 120): d.line([(0, y), (W, y)], fill=(255, 255, 255, 14), width=2)
    for x in range(0, W, 120): d.line([(x, 0), (x, H + 120)], fill=(255, 255, 255, 10), width=2)
    A["grid"] = grid
    rnd = random.Random(7); A["parts"] = []
    for k in range(16):
        s = rnd.choice([90, 160, 260]); A["parts"].append({"g": glow(s, rnd.choice([(255, 200, 87), (120, 220, 200), (255, 255, 255)]), 0.35 if s < 200 else 0.2),
                                                       "x": rnd.randint(-40, W - 60), "sp": rnd.uniform(40, 130), "ph": rnd.uniform(0, H + 400), "s": s})
    ring = Image.new("RGBA", (760, 760), (0, 0, 0, 0)); d = ImageDraw.Draw(ring)
    for r, a in ((360, 60), (300, 40), (230, 28)): d.ellipse([380 - r, 380 - r, 380 + r, 380 + r], outline=(255, 255, 255, a), width=3)
    for ang in range(0, 360, 30):
        x, y = 380 + 360 * math.cos(math.radians(ang)), 380 + 360 * math.sin(math.radians(ang)); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 200, 87, 150))
    A["ring"] = ring
    A["brand"] = word_sprite("Metatya", fl(46), (192, 138, 46))[0]
    A["disc"] = word_sprite("آموزشی است؛ توصیه‌ی سرمایه‌گذاری نیست", fl(30), (160, 185, 178))[0]
    return A

def paste_alpha(base, spr, pos, a):
    if a <= 0: return
    if a >= 0.99: base.paste(spr, pos, spr); return
    al = spr.getchannel("A").point([int(v * a) for v in range(256)]); base.paste(spr.convert("RGB"), pos, al)

# ---------------- زمان‌بندی ----------------
def probe(path):
    try: return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())
    except Exception: return 0.0

async def _tts(text, path, rate):
    import edge_tts
    await edge_tts.Communicate(text, VOICE, rate=rate).save(path)

def tts_all(sentences, tmp):
    if os.environ.get("NO_TTS") == "1": return [None] * len(sentences)
    for rate in ("+0%", "+18%"):
        res = []
        for i, s in enumerate(sentences):
            p = os.path.join(tmp, f"v{i}.mp3")
            try:
                asyncio.run(_tts(re.sub(r"[^\w\s.,؟?!،٫٬/%:-]", " ", s), p, rate)); d = probe(p)
                res.append((p, d) if d > 0.3 else None)
            except Exception as e:
                print("  TTS در دسترس نیست:", str(e)[:70]); return [None] * len(sentences)
        if sum(r[1] for r in res if r) <= 12.5: return res
    return res

def build_timeline(sentences, voices):
    cursor, scenes = 0.5, []
    for i, (s, v) in enumerate(zip(sentences, voices)):
        vd = v[1] if v else 2.6; dur = max(2.6, vd + 0.6) + (1.1 if i == len(sentences) - 1 else 0)
        for size in ((108, 96, 86, 76, 66) if i == 0 else (84, 76, 68, 60, 54)):
            lay, hh = layout(s, size, 800 if i == 0 else 840)
            if hh <= (560 if i == 0 else 620): break
        n = len(lay); span = max(vd * 0.85, 0.6)
        for w in lay: w["t0"] = cursor + 0.12 + span * w["i"] / max(n, 1)
        scenes.append({"s": cursor, "e": cursor + dur, "vs": cursor + 0.15, "vd": vd, "lay": lay, "h": hh, "voice": v[0] if v else None, "kind": i}); cursor += dur
    return scenes, cursor

def make_frame_fn(A, scenes, total, label):
    cta_spr = word_sprite("لینک در بایو · t.me/maytya", fl(54), (26, 20, 5))[0]
    btn = Image.new("RGBA", (cta_spr.width + 90, cta_spr.height + 50), (0, 0, 0, 0)); ImageDraw.Draw(btn).rounded_rectangle([0, 0, btn.width - 1, btn.height - 1], radius=40, fill=(255, 200, 87, 255))
    btn.paste(cta_spr, (45, 25), cta_spr)
    tag = word_sprite(label, fl(40), (255, 200, 87))[0]
    panels = {}
    for sc in scenes:
        if sc["kind"] == 1:
            ph = max(380, sc["h"] + 150); pn = Image.new("RGBA", (W - 110, ph), (0, 0, 0, 0))
            ImageDraw.Draw(pn).rounded_rectangle([0, 0, pn.width - 1, pn.height - 1], radius=48, fill=(255, 255, 255, 24), outline=(255, 255, 255, 60), width=3); panels[id(sc)] = pn
    def frame(t):
        a = 0.5 + 0.5 * math.sin(t * 0.7); im = Image.blend(A["bg1"], A["bg2"], a)
        im.paste(A["grid"], (0, -120 + int((t * 36) % 120)), A["grid"])
        for p in A["parts"]:
            y = int(H + 200 - (t * p["sp"] + p["ph"]) % (H + 400)); im.paste(p["g"], (p["x"], y), p["g"])
        rg = A["ring"].rotate(t * 10, resample=Image.BICUBIC); im.paste(rg, (W // 2 - 380, 760 - 380), rg)
        # نوار پیشرفت
        seg = (W - 120 - 20) // len(scenes)
        for k, sc in enumerate(scenes):
            x0 = 60 + k * (seg + 10); fill = min(max((t - sc["s"]) / (sc["e"] - sc["s"]), 0), 1)
            d = ImageDraw.Draw(im); d.rounded_rectangle([x0, 70, x0 + seg, 78], radius=4, fill=(255, 255, 255, 60) if False else (70, 100, 94)); 
            if fill > 0: d.rounded_rectangle([x0, 70, x0 + int(seg * fill), 78], radius=4, fill=(255, 200, 87))
        im.paste(tag, (W - 60 - tag.width, 100), tag)
        if t < 0.7:  # لوگوی ورودی
            s = A["brand"]; paste_alpha(im, s, ((W - s.width) // 2, 900), 1 - t / 0.7)
        for sc in scenes:
            if sc["s"] - 0.1 <= t <= sc["e"] + 0.1:
                fo = 1.0 if sc is scenes[-1] else min(max((sc["e"] - t) / 0.25, 0), 1)
                lift = 0 if fo >= 1 else int((1 - fo) * -40)
                if sc["kind"] == 1:
                    pn = panels[id(sc)]; pa = ease_out((t - sc["s"]) / 0.4) * fo; py = 840 - pn.height // 2 + int((1 - ease_out((t - sc["s"]) / 0.4)) * 80) + lift; paste_alpha(im, pn, (55, py), pa)
                if sc["kind"] == 0:  # خط تاکیدی متحرک
                    lw = int(540 * ease_out((t - sc["s"] - 0.3) / 0.6)); ImageDraw.Draw(im).rounded_rectangle([W // 2 - lw // 2, 800 + sc["h"] // 2 + 30, W // 2 + lw // 2, 800 + sc["h"] // 2 + 38], radius=4, fill=(255, 200, 87))
                for w in sc["lay"]:
                    k = (t - w["t0"]) / 0.38
                    if k <= 0: continue
                    yo = int((1 - ease_back(k)) * 70); paste_alpha(im, w["spr"], (w["x"], w["y"] + yo + lift), min(k * 2.2, 1) * fo)
                if sc is scenes[-1] and t > sc["e"] - 1.9:  # دکمه‌ی CTA
                    k = ease_back((t - (sc["e"] - 1.9)) / 0.5); sc_ = max(k, 0.01) * (1 + 0.04 * math.sin(t * 7)); bw, bh = int(btn.width * sc_), int(btn.height * sc_)
                    if bw > 4: b2 = btn.resize((bw, bh)); im.paste(b2, ((W - bw) // 2, 1280 - bh // 2), b2)
                    ay = 1170 + int(14 * math.sin(t * 8)); ImageDraw.Draw(im).polygon([(W // 2 - 30, ay), (W // 2 + 30, ay), (W // 2, ay + 38)], fill=(255, 200, 87))
        im.paste(A["brand"], (60, H - 190), A["brand"]); paste_alpha(im, A["disc"], (W - 60 - A["disc"].width, H - 120), 0.85)
        return im
    return frame

# ---------------- صدا ----------------
def audio_graph(scenes, total):
    T = round(total, 2); F = "aformat=sample_rates=44100:channel_layouts=stereo"; g, mix = [], []
    for k, f_ in enumerate((110, 164.81, 220, 329.63)): g.append(f"sine=f={f_}:d={T},{F}[m{k}]")
    g.append(f"[m0][m1][m2][m3]amix=inputs=4:normalize=0:weights='1 0.7 0.6 0.25',tremolo=f=0.3:d=0.5,lowpass=f=1200,aecho=0.8:0.7:500:0.35,volume=0.4,afade=t=in:d=1,afade=t=out:st={max(T-1.6,0)}:d=1.6[music]")
    vin = [(i, sc) for i, sc in enumerate(scenes) if sc["voice"]]
    for j, sc in enumerate(scenes):
        ms = int(max(sc["s"] - 0.12, 0) * 1000)
        g.append(f"anoisesrc=d=0.7:c=pink:r=44100,highpass=f=400,lowpass=f=6000,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.4,volume=0.5,adelay={ms}|{ms},{F}[w{j}]"); mix.append(f"[w{j}]")
    pm = int(max(scenes[-1]["e"] - 1.9, 0) * 1000)
    g.append(f"sine=f=988:d=0.35,afade=t=out:d=0.35,volume=0.3,adelay={pm}|{pm},{F}[pop]"); mix.append("[pop]")
    if vin:
        for n, (i, sc) in enumerate(vin):
            ms = int(sc["vs"] * 1000); g.append(f"[{n + 1}:a]aresample=44100,{F},volume=1.7,adelay={ms}|{ms}[v{n}]")
        g.append("".join(f"[v{n}]" for n in range(len(vin))) + f"amix=inputs={len(vin)}:normalize=0:duration=longest,apad=whole_dur={T},acompressor=threshold=-20dB:ratio=3,asplit=2[voice][vkey]")
        g.append("[music][vkey]sidechaincompress=threshold=0.03:ratio=10:attack=15:release=350[duck]")
        final = "[duck][voice]" + "".join(mix); n_in = 2 + len(mix)
    else:
        final = "[music]" + "".join(mix); n_in = 1 + len(mix)
    g.append(f"{final}amix=inputs={n_in}:normalize=0:duration=longest,alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=9,atrim=0:{T}[aout]")
    return ";".join(g), [sc["voice"] for sc in scenes if sc["voice"]]

def render_video(sentences, out_mp4, label, cover=None):
    tmp = tempfile.mkdtemp(); voices = tts_all(sentences, tmp); scenes, total = build_timeline(sentences, voices)
    A = make_assets(); frame = make_frame_fn(A, scenes, total, label)
    if cover: frame(scenes[0]["s"] + 1.2).save(cover)
    graph, vfiles = audio_graph(scenes, total)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    for v in vfiles: cmd += ["-i", v]
    cmd += ["-filter_complex", graph, "-map", "0:v", "-map", "[aout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", "-movflags", "+faststart", out_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for n in range(int(total * FPS)): p.stdin.write(frame(n / FPS).tobytes())
        p.stdin.close()
    except BrokenPipeError: pass
    if p.wait() != 0: raise RuntimeError("ffmpeg ناموفق بود")
    return total, bool(vfiles)

def main():
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    if "--selftest" in sys.argv:
        im = make_frame_fn(make_assets(), *build_timeline(["یورو/دلار زیر ۱.۱۳۱۲ آمد", "شاخص کل بورس ۷٬۷۶۶٬۵۴۰ واحد", "Bitcoin بالای 86,000 دلار"], [None] * 3), "فارکس")(2.2)
        im.save(os.path.join(ROOT, "out", "selftest.png")); print("selftest.png ساخته شد | RAQM:", RAQM); return
    if "--demo" in sys.argv:
        t0 = time.time(); d, v = render_video(["حد ضررت را چرا جابه‌جا کردی؟", "چون دلت می‌خواهد درست باشی؛ قانون را قبل از ورود بنویس.", "دفترچه‌ی رایگان در لینک بایو."], os.path.join(ROOT, "out", "demo_short.mp4"), "مدیریت ریسک", os.path.join(ROOT, "out", "demo_cover.png"))
        print(f"demo ساخته شد: {d:.1f}s | صدای گوینده: {v} | {time.time()-t0:.0f}s رندر"); return
    data = json.load(open(os.path.join(ROOT, "docs", "content.json"), encoding="utf-8")); site = os.environ.get("SITE_URL", "")
    for key in ("forex", "crypto", "bourse"):
        items = data["sections"].get(key, {}).get("items", [])
        if not items: continue
        it = items[0]
        try:
            d, v = render_video(it["short_script"][:3], os.path.join(ROOT, "out", f"{key}_short.mp4"), NAMES[key], os.path.join(ROOT, "out", f"{key}_cover.png"))
        except Exception as e:
            print("FAIL", key, e); continue
        open(os.path.join(ROOT, "out", f"{key}_upload.txt"), "w", encoding="utf-8").write(
            f"عنوان: {it['title']} | Metatya\n\nتوضیح:\n{it['body'][:300]}\n\nتحلیل کامل و آموزش بیشتر: {site}\nتلگرام: https://t.me/maytya\nاینستاگرام: https://instagram.com/maytyafx\n\n#Metatya #فارکس #کریپتو #بورس #تحلیل_بازار\n⚠️ توصیه سرمایه‌گذاری نیست.\n")
        print(f"ساخته شد: {key} ({d:.1f}s، گوینده: {'بله' if v else 'خیر'})")

import tempfile
if __name__ == "__main__":
    main()
