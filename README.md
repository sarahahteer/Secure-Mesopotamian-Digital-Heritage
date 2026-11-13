# الأرشيف الرقمي الآمن للتراث الرافديني

مشروع تخرج تأسيسي باستخدام Flask وPostgreSQL، بواجهة عربية، ومختبر PHP منفصل للتوعية الأمنية.

## 1) المتطلبات
- Python 3.11 أو أحدث
- PostgreSQL 15 أو أحدث
- PHP 8+ لتشغيل المختبر بشكل منفصل

## 2) إعداد قاعدة البيانات
أنشئ قاعدة ومستخدماً في PostgreSQL (مثال):
```sql
CREATE USER heritage_user WITH PASSWORD 'ضع_كلمة_مرور_قوية';
CREATE DATABASE heritage_archive OWNER heritage_user;
```

## 3) تشغيل Flask
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```
عدّل DATABASE_URL وSECRET_KEY داخل `.env`، ثم:
```bash
python database.py
python app.py
```
افتح `http://127.0.0.1:5000`.

## 4) تشغيل مختبر PHP
من مجلد المشروع:
```bash
php -S 127.0.0.1:8081 -t security_lab
```
ثم افتح `http://127.0.0.1:8081`. لا تعرض المختبر على الإنترنت ولا تربطه بقاعدة بيانات الإنتاج.

## تنبيهات
هذه نسخة هيكل تأسيسي وليست تطبيقاً مكتملاً أو جاهزاً للنشر. لا تحتوي بعد على التسجيل/الدخول، صفحات الإدارة، تدفقات النشر، فحص ClamAV الفعلي، أو اختبارات اختراق مكتملة. لا تضع بيانات أثرية حساسة أو إحداثيات مواقع غير منشورة قبل اعتماد سياسة الجهة المالكة.
