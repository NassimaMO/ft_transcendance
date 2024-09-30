from django.shortcuts import render, redirect
from matchmaker.forms import MatchChoiceForm
from matchmaker.models import GameMode, Connecitvity, Match, MatchChoice
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger('default')

@login_required
def play(request):
    if request.method == 'POST':
        form = MatchChoiceForm(request.POST)
        if form.is_valid():
            form.save()
            cleaned_data = form.clean()
            connect = cleaned_data.get('connect')
            mode = cleaned_data.get('mode')
            mm = cleaned_data.get('mm')
            match_choice = MatchChoice.create(connect=connect, mode=mode, mm=mm)
            match_choice.save()
            if (mode == GameMode.SOLO or connect == Connecitvity.LOCAL) :
                match = Match.objects.create(info=match_choice)
                match.save()
                return redirect('game', match.id)
            else :
                return redirect('matchmaking', match_choice.id)
        else :
            logger.info("invalid form")
    else:
        form = MatchChoiceForm()
    return render(request, "pong/play.html", {'form': form})

@login_required
def game(request, game_id) :
    return render(request, "pong/game.html", {'game_id': game_id})