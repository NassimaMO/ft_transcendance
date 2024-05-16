from django.shortcuts import render
from .models import Author

# Create your views here.

def index(request) :
    return render(request, "index.html")

def rules(request) :
    return render(request, "rules.html")

def about(request) :
    data = dict({"authors": [Author("Nily"), Author("Nassima"), Author("Theo")]})
    return render(request, "about.html", data)

def play(request) :
    return render(request, "play.html")