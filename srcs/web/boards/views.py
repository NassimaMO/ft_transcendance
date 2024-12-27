from django.shortcuts import render

def boards_view(request):
    return render(request, "boards.html")