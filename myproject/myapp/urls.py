from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Dashboard view
    path('create/', views.create_document, name='create_document'),  # Create document view
    path('edit/<int:document_id>/', views.edit_document, name='edit_document'),  # Edit document view
    path('delete/<int:document_id>/', views.delete_document, name='delete_document'),
    path('save/<int:document_id>/', views.save_document, name='save_document'),  # Delete document view
]
