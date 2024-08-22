from django.shortcuts import render, redirect
from .forms import MatchChoiceForm
from matchmaker.models import GameMode, Connecitvity, MatchmakingMode

def play(request):
    if request.method == 'POST':
        form = MatchChoiceForm(request.POST)
        if form.is_valid():
            form.save()
            cleaned_data = form.clean()
            mode = cleaned_data.get('mode')
            connect = cleaned_data.get('connect')
            mm = cleaned_data.get('mm')
            if (mode == GameMode.SOLO or connect == Connecitvity.LOCAL) :
                return redirect('game')
            else :
                return redirect('/match')
    else:
        form = MatchChoiceForm()
    return render(request, "pong/play.html", {'form': form})

def game(request) :
    return (render(request, "pong/game.html"))