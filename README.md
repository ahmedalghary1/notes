# Notebook - مدونة الملاحظات

تطبيق ويب متكامل لإدارة الملاحظات بصيغة Markdown مع دعم كامل للنص المختلط (عربي/إنجليزي).

## المزايا الرئيسية

- ✅ نظام مستخدمين كامل (تسجيل دخول/تسجيل جديد)
- ✅ محرر Markdown مع معاينة حية
- ✅ دعم كامل للنص المختلط عربي/English بدون انعكاس (BiDi)
- ✅ حفظ تلقائي Auto-save
- ✅ تصدير PDF و Markdown
- ✅ مشاركة الملاحظات عبر روابط عامة
- ✅ وسوم Tags وبحث متقدم
- ✅ الوضع الليلي Dark Mode
- ✅ تصميم متجاوب Responsive

## المتطلبات

- Python 3.10+
- Django 4.2+
- Bootstrap 5

## التثبيت

```bash
# تثبيت المكتبات
pip install -r requirements.txt

# إنشاء قاعدة البيانات
python manage.py migrate

# إنشاء مستخدم مدير
python manage.py createsuperuser

# تشغيل المشروع
python manage.py runserver
```

## الاستخدام

1. افتح المتصفح على `http://127.0.0.1:8000`
2. سجل حساب جديد أو سجل دخول
3. ابدأ بإنشاء ملاحظاتك بصيغة Markdown

## البنية التقنية

- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5 RTL
- **Markdown**: markdown2 + marked.js
- **Code Highlighting**: highlight.js
- **PDF Export**: xhtml2pdf

## الأمان

- ✅ حماية من XSS عبر bleach
- ✅ حماية CSRF
- ✅ صلاحيات الوصول - كل مستخدم يرى ملاحظاته فقط
- ✅ تعقيم HTML الناتج من Markdown

## الترخيص

MIT License
