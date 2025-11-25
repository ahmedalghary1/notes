from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Note


class RegisterForm(UserCreationForm):
    """نموذج التسجيل"""
    email = forms.EmailField(
        required=True,
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني',
            'dir': 'auto'
        })
    )
    
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اختر اسم المستخدم',
            'dir': 'auto'
        })
    )
    
    password1 = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
    
    password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """نموذج تسجيل الدخول"""
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم المستخدم',
            'dir': 'auto'
        })
    )
    
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'كلمة المرور'
        })
    )


class NoteForm(forms.ModelForm):
    """نموذج إنشاء وتعديل الملاحظات"""
    title = forms.CharField(
        label='العنوان',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'عنوان الملاحظة',
            'dir': 'auto',
            'id': 'note-title'
        })
    )
    
    content_md = forms.CharField(
        label='المحتوى',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 15,
            'placeholder': 'اكتب ملاحظتك بصيغة Markdown...',
            'dir': 'auto',
            'id': 'markdown-editor'
        }),
        required=False
    )
    
    is_public = forms.BooleanField(
        label='مشاركة عامة (يمكن لأي شخص رؤية الملاحظة عبر رابط)',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'is-public'
        })
    )
    
    is_favorite = forms.BooleanField(
        label='إضافة إلى المفضلة',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'is-favorite'
        })
    )
    
    class Meta:
        model = Note
        fields = ['title', 'content_md', 'is_public', 'is_favorite']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة حقل الوسوم يدوياً
        if self.instance and self.instance.pk:
            self.fields['tags_field'] = forms.CharField(
                label='الوسوم',
                required=False,
                initial=', '.join([tag.name for tag in self.instance.tags.all()]),
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'وسم1, وسم2, وسم3',
                    'dir': 'auto',
                    'id': 'tags-input'
                })
            )
        else:
            self.fields['tags_field'] = forms.CharField(
                label='الوسوم',
                required=False,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'وسم1, وسم2, وسم3',
                    'dir': 'auto',
                    'id': 'tags-input'
                })
            )
