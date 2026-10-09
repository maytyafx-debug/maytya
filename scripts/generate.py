"""تولید روزانه محتوای همه حوزه‌ها -> docs/content.json   (فقط سرویس‌های رایگان)
زنجیره ارائه‌دهنده (اولین کلید موجود اول، در صورت خطا یا خروجی بی‌کیفیت نفر بعدی):
  1) Google Gemini  GEMINI_API_KEY   (بهترین فارسی)
  2) Cloudflare     CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID
  3) Mistral        MISTRAL_API_KEY
بازارها: تیتر خبرهای روز از RSS رایگان؛ مدل فقط بر پایه همان‌ها می‌نویسد.
دروازه کیفیت: ساختار، زبان فارسی، طول، عبارت‌های ممنوع؛ هشدار ریسک همیشه با کد اضافه می‌شود."""
import os, sys, json, re, time, datetime
import xml.etree.ElementTree as ET
import requests
from sections import SECTIONS

DRY = "--dry" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "..", "out" if DRY else "docs", "dry-content.json" if DRY else "content.json")  # حالت --dry هرگز فایل زنده را عوض نمی‌کند
KEEP = 40
DEAD, FAILS = set(), {}


def E(name, default=""):
    # مقدار خالی یا فاصله‌دار (مثلاً متغیری که در GitHub تعریف شده ولی خالی است یا با Enter کپی شده) مساوی «تنظیم نشده» است
    return (os.environ.get(name) or default).strip()


GN = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{lang}"
FEEDS = {
    "forex":  [GN.format(q="forex+EURUSD+dollar+gold+Fed", hl="en-US", gl="US", lang="en"), "https://www.fxstreet.com/rss/news"],
    "crypto": [GN.format(q="bitcoin+price+ETF", hl="en-US", gl="US", lang="en"), "https://cointelegraph.com/rss"],
    "bourse": [GN.format(q="%D8%B4%D8%A7%D8%AE%D8%B5+%DA%A9%D9%84+%D8%A8%D9%88%D8%B1%D8%B3+%D8%AA%D9%87%D8%B1%D8%A7%D9%86", hl="fa", gl="IR", lang="fa")],
}
DISCLAIMER = {
    "fin": "این محتوا آموزشی است و توصیه مالی یا سرمایه‌گذاری نیست.",
} # <--- این آکولاد بسته اضافه شد تا خطای سینتکس برطرف شود
