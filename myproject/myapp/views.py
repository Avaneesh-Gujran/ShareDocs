from django.shortcuts import render
from .forms import DocumentForm
# Create your views here.

from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from .models import Document
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document, Cursor
from .forms import SignupForm
from .models import User
from django.contrib import messages
from django.template.loader import render_to_string

from xhtml2pdf import pisa
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

def dashboard(request):
    documents = Document.objects.all()
    return render(request, 'dashboard.html', {'documents': documents})

def create_document(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save()
            return redirect('edit_document', document_id=document.id)
    else:
        form = DocumentForm()
    return render(request, 'create_document.html', {'form': form})

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


def get_document_state(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        cursors = document.cursors.all()
        cursor_data = [
            {'user_id': cursor.user_id, 'cursor_position': cursor.cursor_position}
            for cursor in cursors
        ]
        return JsonResponse({
            'content': document.content,
            'cursors': cursor_data
        })
    except Document.DoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)

@csrf_exempt
def update_document_content(request, document_id):
    if request.method == "POST":
        try:
            document = Document.objects.get(id=document_id)
            document.content = request.POST.get('content', '')
            document.save()
            return JsonResponse({'status': 'success'})
        except Document.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def update_cursor(request, document_id):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        cursor_position = request.POST.get('cursor_position')
        try:
            document = Document.objects.get(id=document_id)
            cursor, created = Cursor.objects.update_or_create(
                document=document,
                user_id=user_id,
                defaults={'cursor_position': cursor_position}
            )
            return JsonResponse({'status': 'success'})
        except Document.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)


import bleach

def clean_html(raw_html):
    # Define allowed tags and attributes
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'div', 'span', 'font']
    allowed_attributes = {
        'span': ['style'],
        'font': ['face', 'color', 'size'],
        'div': ['style'],
        'p': ['style'],
    }

    # Clean the HTML
    return bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attributes, strip=True)



def export_to_pdf(request, document_id):
    # Fetch the document from the database
    document = Document.objects.get(id=document_id)

    # Clean the document content
    cleaned_content = clean_html(document.content)

    # Render the template with cleaned content
    html_content = render_to_string('document_pdf.html', {'document': document, 'cleaned_content': cleaned_content})

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document.title}.pdf"'

    # Use pisa to convert HTML to PDF
    pisa_status = pisa.CreatePDF(html_content, dest=response)

    # Handle errors
    if pisa_status.err:
        return HttpResponse('An error occurred while generating the PDF', status=500)

    return response

def user_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            
            if user.password == password:  # Compare plaintext password
                login(request, user)  # Django session login
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid email or password.")
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists.")
            return redirect('signup')

        # Store password as plaintext
        user = User.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            password=password  # Store password directly
        )
        messages.success(request, "Signup successful! You can now log in.")
        return redirect('login')

    return render(request, 'signup.html')

