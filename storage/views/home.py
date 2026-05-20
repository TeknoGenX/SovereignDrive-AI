from django.shortcuts import render

def home(request):
    """
    View untuk menampilkan Landing Page utama (Awan Enterprise).
    """
    return render(request, 'storage/home.html')