from django.contrib import admin
from .models import Note, NoteVersion


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """تكوين صفحة الإدارة للملاحظات"""
    list_display = ('title', 'owner', 'is_public', 'is_favorite', 'views', 'created_at', 'updated_at')
    list_filter = ('is_public', 'is_favorite', 'created_at', 'owner')
    search_fields = ('title', 'content_md', 'owner__username')
    readonly_fields = ('content_html', 'public_uuid', 'created_at', 'updated_at', 'views')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('owner', 'title', 'content_md', 'content_html')
        }),
        ('الوسوم والإعدادات', {
            'fields': ('tags', 'is_public', 'is_favorite')
        }),
        ('المعلومات الإضافية', {
            'fields': ('public_uuid', 'views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NoteVersion)
class NoteVersionAdmin(admin.ModelAdmin):
    """تكوين صفحة الإدارة لنسخ الملاحظات"""
    list_display = ('note', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('note__title', 'content_md')
    readonly_fields = ('note', 'content_md', 'created_at')
