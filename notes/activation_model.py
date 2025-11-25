# Activation Code model for email verification

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string


class ActivationCode(models.Model):
    """كود التفعيل للتحقق من البريد الإلكتروني"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activation_codes')
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
