# ===== دليل إعداد المشروع للإنتاج (Production) =====

## 📋 الخطوات المطلوبة قبل الرفع على السيرفر

### 1️⃣ تثبيت Whitenoise (لخدمة الملفات الثابتة)

```bash
pip install whitenoise
```

أضف إلى `requirements.txt`:
```
whitenoise==6.6.0
```

---

### 2️⃣ تعديل `settings.py`

#### أ) إضافة Whitenoise للـ MIDDLEWARE

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← أضف هنا
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... باقي middleware
]
```

#### ب) إعدادات الأمان للإنتاج

```python
import os

# قراءة من متغيرات البيئة
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
# مثال: ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', '123.45.67.89']

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-...')
```

#### ج) إعدادات Static Files للإنتاج

```python
# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### د) إعدادات قاعدة البيانات (إذا كنت تستخدم PostgreSQL)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

#### هـ) إعدادات HTTPS والأمان

```python
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

### 3️⃣ جمع الملفات الثابتة

قبل الرفع، قم بتشغيل:

```bash
python manage.py collectstatic --noinput
```

هذا سينسخ جميع الملفات من `static/` و `staticfiles_dirs` إلى `staticfiles/`

---

### 4️⃣ متغيرات البيئة (Environment Variables)

#### استخدام ملف `.env`

تثبيت `python-decouple`:
```bash
pip install python-decouple
```

إنشاء ملف `.env` في جذر المشروع:
```env
DEBUG=False
SECRET_KEY=your-very-secret-key-here-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=notebook_db
DB_USER=db_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432
```

في `settings.py`:
```python
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

**⚠️ مهم:** أضف `.env` إلى `.gitignore`

---

### 5️⃣ إعداد خادم الويب (Web Server)

#### أ) استخدام Gunicorn

تثبيت:
```bash
pip install gunicorn
```

تشغيل:
```bash
gunicorn notebook_project.wsgi:application --bind 0.0.0.0:8000
```

#### ب) Nginx Configuration (مثال)

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/notebook/staticfiles/;
    }

    location /media/ {
        alias /path/to/notebook/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 6️⃣ Checklist قبل الرفع ✅

- [ ] `DEBUG = False` في الإنتاج
- [ ] `ALLOWED_HOSTS` محدد بشكل صحيح
- [ ] `SECRET_KEY` مخزن بشكل آمن (في متغيرات البيئة)
- [ ] Whitenoise مثبت ومفعّل
- [ ] `collectstatic` تم تشغيله
- [ ] قاعدة البيانات محددة (PostgreSQL/MySQL للإنتاج)
- [ ] HTTPS مفعّل (SSL Certificate)
- [ ] `.env` في `.gitignore`
- [ ] `requirements.txt` محدث
- [ ] Nginx/Apache مضبوط
- [ ] Gunicorn أو uWSGI مثبت
- [ ] Backups مجدولة

---

### 7️⃣ أوامر مفيدة

```bash
# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# إنشاء migrations
python manage.py makemigrations

# تطبيق migrations
python manage.py migrate

# إنشاء superuser
python manage.py createsuperuser

# تشغيل مع Gunicorn
gunicorn notebook_project.wsgi:application --workers 3 --bind 0.0.0.0:8000

# تشغيل في الخلفية
gunicorn notebook_project.wsgi:application --workers 3 --bind 0.0.0.0:8000 --daemon
```

---

### 8️⃣ ملف `requirements.txt` المحدث

```txt
Django==5.2.8
markdown2==2.5.2
bleach==6.2.0
django-taggit==6.1.0
Pillow==11.0.0
reportlab==4.2.5
whitenoise==6.6.0
gunicorn==23.0.0
python-decouple==3.8
psycopg2-binary==2.9.10  # إذا كنت تستخدم PostgreSQL
```

---

### 9️⃣ خيارات الاستضافة المقترحة

1. **VPS (Digital Ocean, Linode, Vultr)**
   - تحكم كامل
   - يحتاج إعداد يدوي
   - تكلفة: $5-20/شهر

2. **PaaS (Heroku, Railway, Render)**
   - سهل الإعداد
   - يدير Infrastructure تلقائياً
   - تكلفة: $0-25/شهر (حسب الاستخدام)

3. **AWS/GCP/Azure**
   - قابل للتوسع
   - معقد قليلاً
   - تكلفة متغيرة

---

### 🔟 نصيحة إضافية للبريد الإلكتروني

إذا كنت ستستخدم نظام التحقق بالبريد، ستحتاج:

```python
# في settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

في `.env`:
```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## ✅ الخلاصة

**الإعدادات الحالية:**
- ✅ جيدة للتطوير المحلي
- ⚠️ تحتاج تعديلات للإنتاج

**أهم التعديلات المطلوبة:**
1. إضافة `/` لـ `STATIC_URL` و `MEDIA_URL`
2. تثبيت وتفعيل Whitenoise
3. استخدام متغيرات البيئة للإعدادات الحساسة
4. ضبط `ALLOWED_HOSTS` و `DEBUG=False`
5. تشغيل `collectstatic`

**بعد التطبيق:**
المشروع جاهز للرفع على أي خادم! 🚀
