from django.shortcuts import render
from .models import Author
from django.contrib.staticfiles import finders
from django.http import HttpResponse

def index(request) :
    return render(request, "index.html")

def rules(request) :
    return render(request, "rules.html")

def about(request) :
    data = dict({"authors": [Author("Nily"), Author("Nassima"), Author("Theo")]})
    return render(request, "about.html", data)

def play(request) :
    return render(request, "play.html")

def media(request, file_path):
    static_path = finders.find(file_path)
    if static_path:
        with open(static_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/png")
    else:
        raise HttpResponse(status=404)