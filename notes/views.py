from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json

from .models import Note, NoteVersion
from .forms import RegisterForm, LoginForm, NoteForm


# ===== Authentication Views =====

def register_view(request):
    """صفحة التسجيل"""
    if request.user.is_authenticated:
        return redirect('notes_list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'تم إنشاء حسابك بنجاح! مرحباً بك في Notebook')
            return redirect('notes_list')
    else:
        form = RegisterForm()
    
    return render(request, 'notes/register.html', {'form': form})


def login_view(request):
    """صفحة تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('notes_list')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'أهلاً بك {username}!')
                return redirect('notes_list')
    else:
        form = LoginForm()
    
    return render(request, 'notes/login.html', {'form': form})


def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح')
    return redirect('login')


@login_required
def profile_view(request):
    """صفحة الملف الشخصي"""
    notes = request.user.notes.all()
    stats = {
        'total_notes': notes.count(),
        'favorite_notes': notes.filter(is_favorite=True).count(),
        'public_notes': notes.filter(is_public=True).count(),
        'total_views': sum(note.views for note in notes),
    }
    return render(request, 'notes/profile.html', {'stats': stats})


def markdown_docs_view(request):
    """صفحة دليل Markdown"""
    return render(request, 'notes/markdown_docs.html')


# ===== Notes CRUD Views =====

@login_required
def notes_list_view(request):
    """قائمة الملاحظات"""
    notes = request.user.notes.all()
    
    # البحث
    search_query = request.GET.get('search', '')
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) | 
            Q(content_md__icontains=search_query)
        )
    
    # فلترة حسب الوسم
    tag = request.GET.get('tag', '')
    if tag:
        notes = notes.filter(tags__name__in=[tag])
    
    # فلترة المفضلة
    favorites_only = request.GET.get('favorites', '')
    if favorites_only:
        notes = notes.filter(is_favorite=True)
    
    # الترتيب
    sort_by = request.GET.get('sort', '-updated_at')
    valid_sorts = ['-updated_at', 'updated_at', '-created_at', 'created_at', 'title', '-title', '-views']
    if sort_by in valid_sorts:
        notes = notes.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(notes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # جمع كل الوسوم
    all_tags = set()
    for note in request.user.notes.all():
        all_tags.update(note.tags.names())
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_tag': tag,
        'all_tags': sorted(all_tags),
        'favorites_only': favorites_only,
        'sort_by': sort_by,
    }
    
    return render(request, 'notes/notes_list.html', context)


@login_required
def note_detail_view(request, pk):
    """عرض تفاصيل الملاحظة"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    note.increment_views()
    
    # جلب النسخ السابقة
    versions = note.versions.all()[:5]
    
    context = {
        'note': note,
        'versions': versions,
    }
    
    return render(request, 'notes/note_detail.html', context)


@login_required
def note_create_view(request):
    """إنشاء ملاحظة جديدة"""
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.owner = request.user
            note.save()
            
            # حفظ الوسوم
            tags_field = form.cleaned_data.get('tags_field', '')
            if tags_field:
                tags_list = [tag.strip() for tag in tags_field.split(',') if tag.strip()]
                note.tags.set(*tags_list)
            
            messages.success(request, 'تم إنشاء الملاحظة بنجاح!')
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm()
    
    return render(request, 'notes/note_edit.html', {
        'form': form,
        'is_new': True
    })


@login_required
def note_edit_view(request, pk):
    """تعديل ملاحظة"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save()
            
            # حفظ الوسوم
            tags_field = form.cleaned_data.get('tags_field', '')
            if tags_field:
                tags_list = [tag.strip() for tag in tags_field.split(',') if tag.strip()]
                note.tags.set(*tags_list)
            else:
                note.tags.clear()
            
            messages.success(request, 'تم تحديث الملاحظة بنجاح!')
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note)
    
    return render(request, 'notes/note_edit.html', {
        'form': form,
        'note': note,
        'is_new': False
    })


@login_required
def note_delete_view(request, pk):
    """حذف ملاحظة"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'تم حذف الملاحظة بنجاح!')
        return redirect('notes_list')
    
    return render(request, 'notes/note_confirm_delete.html', {'note': note})


# ===== AJAX Views =====

@login_required
@require_POST
def toggle_favorite_view(request, pk):
    """تبديل حالة المفضلة"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    note.is_favorite = not note.is_favorite
    note.save(update_fields=['is_favorite'])
    
    return JsonResponse({
        'success': True,
        'is_favorite': note.is_favorite
    })


@login_required
@require_POST
def autosave_view(request, pk):
    """حفظ تلقائي للملاحظة"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    
    try:
        data = json.loads(request.body)
        note.title = data.get('title', note.title)
        note.content_md = data.get('content_md', note.content_md)
        note.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم الحفظ تلقائياً',
            'timestamp': note.updated_at.isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ===== Public Note View =====

def public_note_view(request, uuid):
    """عرض الملاحظة العامة"""
    note = get_object_or_404(Note, public_uuid=uuid, is_public=True)
    note.increment_views()
    
    return render(request, 'notes/public_note.html', {'note': note})


# ===== Export Views =====

@login_required
def export_markdown_view(request, pk):
    """تصدير الملاحظة كـ Markdown"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    
    response = HttpResponse(note.content_md, content_type='text/markdown')
    response['Content-Disposition'] = f'attachment; filename="{note.title or "note"}.md"'
    
    return response


@login_required
def export_pdf_view(request, pk):
    """تصدير الملاحظة كـ PDF"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    
    # إنشاء buffer للـ PDF
    buffer = BytesIO()
    
    # إنشاء المستند
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # الحاوية للعناصر
    story = []
    
    # الأنماط
    styles = getSampleStyleSheet()
    
    # نمط للعنوان (RTL)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_RIGHT,
        fontSize=18,
        spaceAfter=30,
    )
    
    # نمط للمحتوى (RTL)
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['BodyText'],
        alignment=TA_RIGHT,
        fontSize=12,
        leading=20,
    )
    
    # إضافة العنوان
    title = Paragraph(note.title or 'ملاحظة بدون عنوان', title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # إضافة المحتوى (تحويل HTML إلى نص بسيط)
    # ملاحظة: reportlab لا يدعم HTML المعقد، لذا سنستخدم النص الأصلي
    content_lines = note.content_md.split('\n')
    for line in content_lines:
        if line.strip():
            p = Paragraph(line, content_style)
            story.append(p)
            story.append(Spacer(1, 6))
    
    # بناء PDF
    doc.build(story)
    
    # إرجاع الملف
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'{note.title or "note"}.pdf')
