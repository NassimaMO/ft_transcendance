from django.shortcuts import render, redirect # type: ignore
from django.utils import timezone
from django.contrib.auth.decorators import login_required # type: ignore
import logging

logger = logging.getLogger('default')

@login_required
def game(request, game_id) :
    return render(request, "pong/game.html", {'game_id': game_id, "timestamp": int(timezone.now().timestamp())})