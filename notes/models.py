from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager
import markdown2
import bleach
import uuid


class Note(models.Model):
    """
    نموذج الملاحظة - يدعم Markdown مع حماية XSS
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', verbose_name='المالك')
    title = models.CharField(max_length=200, verbose_name='العنوان')
    content_md = models.TextField(verbose_name='المحتوى (Markdown)', blank=True)
    content_html = models.TextField(verbose_name='المحتوى (HTML)', blank=True, editable=False)
    tags = TaggableManager(verbose_name='الوسوم', blank=True)
    
    is_public = models.BooleanField(default=False, verbose_name='مشاركة عامة')
    public_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='الرابط العام')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    views = models.IntegerField(default=0, verbose_name='عدد المشاهدات')
    is_favorite = models.BooleanField(default=False, verbose_name='مفضلة')
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'ملاحظة'
        verbose_name_plural = 'الملاحظات'
    
    def __str__(self):
        return self.title or f'ملاحظة #{self.id}'
    
    def save(self, *args, **kwargs):
        """
        تحويل Markdown إلى HTML مع تعقيم للحماية من XSS
        """
        # تحويل Markdown إلى HTML
        if self.content_md:
            html = markdown2.markdown(
                self.content_md,
                extras=[
                    'fenced-code-blocks',
                    'tables',
                    'break-on-newline',
                    'code-friendly',
                    'cuddled-lists',
                    'header-ids',
                    'nofollow',
                    'task_list'
                ]
            )
            
            # تعقيم HTML للحماية من XSS
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'blockquote', 'code', 'pre', 'hr', 'div', 'span',
                'ul', 'ol', 'li', 'a', 'img',
                'table', 'thead', 'tbody', 'tr', 'th', 'td',
                'del', 'ins', 'sup', 'sub'
            ]
            
            allowed_attributes = {
                '*': ['class', 'id', 'dir'],
                'a': ['href', 'title', 'rel'],
                'img': ['src', 'alt', 'title', 'width', 'height'],
                'code': ['class'],
                'pre': ['class'],
            }
            
            self.content_html = bleach.clean(
                html,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True
            )
        else:
            self.content_html = ''
        
        # إنشاء نسخة قبل الحفظ (إذا كانت الملاحظة موجودة مسبقاً)
        if self.pk:
            try:
                old_note = Note.objects.get(pk=self.pk)
                if old_note.content_md != self.content_md:
                    NoteVersion.objects.create(
                        note=self,
                        content_md=old_note.content_md
                    )
            except Note.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def increment_views(self):
        """زيادة عدد المشاهدات"""
        self.views += 1
        self.save(update_fields=['views'])


class NoteVersion(models.Model):
    """
    نموذج نسخ الملاحظات - للاحتفاظ بالنسخ السابقة
    """
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='versions', verbose_name='الملاحظة')
    content_md = models.TextField(verbose_name='المحتوى (Markdown)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نسخة ملاحظة'
        verbose_name_plural = 'نسخ الملاحظات'
    
    def __str__(self):
        return f'{self.note.title} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


from datetime import timedelta
import random
import string


class ActivationCode(models.Model):
    """كود التفعيل للتحقق من البريد الإلكتروني"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activation_codes', verbose_name='المستخدم')
    code = models.CharField(max_length=6, verbose_name='كود التفعيل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    expires_at = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    is_used = models.BooleanField(default=False, verbose_name='تم الاستخدام')
    
    class Meta:
        verbose_name = 'كود تفعيل'
        verbose_name_plural = 'أكواد التفعيل'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.code}'
    
    @staticmethod
    def generate_code():
        """إنشاء كود عشوائي من 6 أرقام"""
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_for_user(cls, user):
        """إنشاء كود تفعيل جديد للمستخدم"""
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=15)
        
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """التحقق من صلاحية الكود"""
        if self.is_used:
            return False, 'تم استخدام هذا الكود من قبل'
        
        if timezone.now() > self.expires_at:
            return False, 'انتهت صلاحية الكود'
        
        return True, 'الكود صالح'
    
    def mark_as_used(self):
        """تعليم الكود كمستخدم"""
        self.is_used = True
        self.save(update_fields=['is_used'])
