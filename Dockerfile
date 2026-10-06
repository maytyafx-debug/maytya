# استفاده از ایمیج پایه پایتون
FROM python:3.12-slim

# تنظیم پوشه کاری
WORKDIR /app

# کپی کردن فایل‌های پروژه
COPY . .

# نصب پکیج‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# باز کردن پورت 7860 که Hugging Face Spaces انتظار داره
EXPOSE 7860

# اجرای ربات با gunicorn
CMD ["gunicorn", "bot:flask_app", "--bind", "0.0.0.0:7860"]
