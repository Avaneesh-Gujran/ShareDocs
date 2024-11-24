from django.urls import path
from . import views


urlpatterns = [
    path('', views.user_login, name='login'),  # Dashboard view
    path('create/', views.create_document, name='create_document'),  # Create document view
    path('edit/<int:document_id>/', views.edit_document, name='edit_document'),  # Edit document view
    path('delete/<int:document_id>/', views.delete_document, name='delete_document'),
    path('save/<int:document_id>/', views.save_document, name='save_document'), 
    path('document/<int:document_id>/export_pdf/', views.export_to_pdf, name='export_to_pdf'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'), # Delete document view
   
]
