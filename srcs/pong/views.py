from django.shortcuts import render, redirect
from .forms import MatchChoiceForm

def play(request):
    if request.method == 'POST':
        form = MatchChoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('match')
    else:
        form = MatchChoiceForm()
    return render(request, "pong/play.html", {'form': form})

def game(request) :
    return (render(request, "pong/game.html"))

def private(request) :
    return (render(request, "pong/private.html"))