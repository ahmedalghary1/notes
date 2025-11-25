from django.urls import path
from . import views
from .home_views import home_view

urlpatterns = [
    # Home
    path('', home_view, name='home'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('docs/', views.markdown_docs_view, name='markdown_docs'),
    
    # Notes CRUD URLs
    path('notes/', views.notes_list_view, name='notes_list'),
    path('note/<int:pk>/', views.note_detail_view, name='note_detail'),
    path('note/new/', views.note_create_view, name='note_create'),
    path('note/<int:pk>/edit/', views.note_edit_view, name='note_edit'),
    path('note/<int:pk>/delete/', views.note_delete_view, name='note_delete'),
    
    # AJAX URLs
    path('note/<int:pk>/toggle-favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('note/<int:pk>/autosave/', views.autosave_view, name='autosave'),
    
    # Public sharing
    path('share/<uuid:uuid>/', views.public_note_view, name='public_note'),
    
    # Export URLs
    path('note/<int:pk>/export/markdown/', views.export_markdown_view, name='export_markdown'),
    path('note/<int:pk>/export/pdf/', views.export_pdf_view, name='export_pdf'),
]
