from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Document

def dashboard(request):
    documents = Document.objects.all()
    return render(request, 'dashboard.html', {'documents': documents})

def create_document(request):
    document = Document.objects.create()
    return redirect('edit_document', document_id=document.id)

def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        document.content = request.POST.get('content')
        document.save()
        return redirect('dashboard')
    return render(request, 'edit_document.html', {'document': document})

def save_document(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, id=document_id)
        document.content = request.POST.get('content')
        document.save()
        return redirect('dashboard')

def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    document.delete()
    return redirect('dashboard')
