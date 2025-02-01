from django.shortcuts import render, redirect # type: ignore
from matchmaker.forms import MatchChoiceForm
from matchmaker.models import Match, MatchChoice
from django.utils import timezone
from django.contrib.auth.decorators import login_required # type: ignore
import logging

logger = logging.getLogger('default')

@login_required
def game(request, game_id) :
    return render(request, "pong/game.html", {'game_id': game_id, "timestamp": int(timezone.now().timestamp())})

@login_required
def play(request) :
    return render(request, "pong/game.html", {"timestamp": int(timezone.now().timestamp())})