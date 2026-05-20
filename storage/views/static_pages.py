from django.shortcuts import render
from django.utils import timezone

def privacy_policy(request):
    return render(request, 'storage/privacy.html', {'today': timezone.now()})

def terms_of_service(request):
    return render(request, 'storage/terms.html', {'today': timezone.now()})

def help_center(request):
    return render(request, 'storage/help.html')

def user_guide(request):
    return render(request, 'storage/user_guide.html')

def security_docs(request):
    return render(request, 'storage/security_docs.html')
