#!/usr/bin/env bash
# معادل مرحله‌های daily.yml. مراحل اصلی متوقف‌کننده‌اند؛ بقیه فقط هشدار می‌دهند (مثل continue-on-error).
set -u
cd /app
mkdir -p out private_packs assets/fonts

run_required() {
  echo "== $1"
  shift
  "$@" || { echo "خطا در مرحله‌ی اصلی؛ اجرا متوقف شد."; exit 1; }
}

run_optional() {
  echo "== $1"
  shift
  "$@" || echo "هشدار: این مرحله ناموفق بود، ادامه می‌دهیم."
}

# ۱) جمع‌آوری داده (اختیاری)
run_optional "collector" python scripts/collector.py

# ۲) تولید محتوا (اصلی)
run_required "generate" python scripts/generate.py

# ۳) فونت وزیرمتن (اختیاری؛ اگر نبود DejaVu استفاده می‌شود)
echo "== font"
curl -fsSL --max-time 60 -o assets/fonts/Vazirmatn-Regular.ttf \
  "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf" || true
if [ ! -s assets/fonts/Vazirmatn-Regular.ttf ] || \
   [ "$(head -c 4 assets/fonts/Vazirmatn-Regular.ttf | od -An -tx1 | tr -d ' \n')" != "00010000" ]; then
  rm -f assets/fonts/Vazirmatn-Regular.ttf
fi

# ۴) ساخت صفحات سایت (اصلی)
run_required "build_pages" python scripts/build_pages.py

# ۶) ویدیو کوتاه (اختیاری)
run_optional "make_short" python scripts/make_short.py

# ۷) ارسال به تلگرام (اختیاری)
run_optional "post_telegram" python scripts/post_telegram.py

# ۸) ربات جستجوگر فرصت (اختیاری)
run_optional "radar" python scripts/radar.py

echo "== done"
ls -la docs data 2>/dev/null | head -5
