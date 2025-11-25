# 🚂 دليل الرفع على Railway

## الخطوات السريعة

### 1️⃣ تسجيل الدخول في Railway
1. اذهب إلى https://railway.app
2. سجل دخول باستخدام GitHub
3. انقر على "New Project"

### 2️⃣ إنشاء مشروع جديد
1. اختر "Deploy from GitHub repo"
2. اختر repository الخاص بك
3. أو استخدم "Deploy from local"

### 3️⃣ إضافة PostgreSQL Database
1. في project dashboard → انقر "New"
2. اختر "Database" → "Add PostgreSQL"
3. Railway سيوفر `DATABASE_URL` تلقائياً

### 4️⃣ إضافة Environment Variables
في Settings → Variables، أضف:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

**لتوليد SECRET_KEY:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5️⃣ Deploy!
- Railway سيكتشف Procfile تلقائياً
- سيقوم بتشغيل migrations تلقائياً
- سيجمع static files تلقائياً

---

## ✅ الملفات المطلوبة (تم إنشاؤها)

- ✅ `Procfile` - يخبر Railway كيف يشغل التطبيق
- ✅ `runtime.txt` - يحدد إصدار Python
- ✅ `requirements.txt` - المكتبات المطلوبة
- ✅ `railway.json` - إعدادات Railway
- ✅ `.env.example` - مثال للمتغيرات

---

## 🔧 إعدادات settings.py

تم تحديث `settings.py` بـ:
- ✅ Whitenoise لخدمة static files
- ✅ دعم PostgreSQL من `DATABASE_URL`
- ✅ متغيرات البيئة (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- ✅ إعدادات الأمان للإنتاج (HTTPS, HSTS, etc.)
- ✅ Logging للمراقبة

---

## 📝 بعد الرفع

### إنشاء Superuser
```bash
# في Railway dashboard → انقر على service
# اذهب لـ Settings → Variables
# أضف متغير جديد:
DJANGO_SUPERUSER_PASSWORD=your-admin-password
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com

# ثم في terminal:
railway run python manage.py createsuperuser --noinput
```

أو باستخدام Railway CLI:
```bash
railway run python manage.py createsuperuser
```

### تشغيل أوامر Django
```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# تشغيل الأوامر
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
railway run python manage.py createsuperuser
```

---

## 🌐 الوصول للموقع

بعد Deploy، ستحصل على رابط:
```
https://your-app-name.up.railway.app
```

يمكنك:
1. إضافة Custom Domain في Settings
2. SSL يتم تفعيله تلقائياً
3. مراقبة logs في Deployments tab

---

## 🔍 Troubleshooting

### المشكلة: Static files لا تظهر
**الحل:**
```bash
railway run python manage.py collectstatic --noinput
```

### المشكلة: Database errors
**الحل:**
- تأكد من إضافة PostgreSQL service
- تحقق من `DATABASE_URL` في Variables

### المشكلة: Application Error
**الحل:**
- افتح Deployments → View Logs
- ابحث عن الخطأ
- تأكد من `DEBUG=False` و `ALLOWED_HOSTS` صحيح

---

## 💡 نصائح

1. **استخدم Railway CLI** للتحكم الأفضل
2. **افحص Logs** بانتظام
3. **اجعل Backups** من قاعدة البيانات
4. **استخدم Custom Domain** للإنتاج
5. **راقب Usage** لتجنب تجاوز Free tier

---

## 🎯 Quick Commands

```bash
# Clone and setup
git clone your-repo
cd your-repo
pip install -r requirements.txt

# Local test
python manage.py migrate
python manage.py collectstatic
python manage.py runserver

# Deploy to Railway
railway login
railway init
railway up
```

---

## ✅ Checklist النهائي

- [ ] تم Push للـ repo على GitHub
- [ ] تم إنشاء project على Railway
- [ ] تم إضافة PostgreSQL
- [ ] تم إضافة Environment Variables
- [ ] تم Deploy بنجاح
- [ ] تم تشغيل migrations
- [ ] تم إنشاء superuser
- [ ] الموقع يعمل على Railway URL
- [ ] Static files تظهر بشكل صحيح

---

## 🚀 جاهز!

مشروعك الآن online على Railway! 🎉

**Railway URL:** https://your-app.up.railway.app
**Admin Panel:** https://your-app.up.railway.app/admin/

---

## 📞 المساعدة

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
