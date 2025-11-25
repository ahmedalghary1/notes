from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home_view(request):
    """الصفحة الرئيسية - تحويل للملاحظات أو صفحة الدخول"""
    if request.user.is_authenticated:
        return redirect('notes_list')
    else:
        return redirect('login')
