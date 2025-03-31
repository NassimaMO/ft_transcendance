from django.shortcuts import render, redirect # type: ignore
from django.utils import timezone
from django.contrib.auth.decorators import login_required # type: ignore
from matchmaker.models import Match
import logging

logger = logging.getLogger('default')

@login_required
def game(request, game_id):
    match = Match.objects.get(id=game_id)
    if not match:
        return redirect("lobby-home")
    if not match.is_in_match(request.user):
        return redirect("lobby-home")
    context = {
        'game_id': game_id,
        'user_id': request.user.id,
        "timestamp": int(timezone.now().timestamp())
    }
    return render(request, "pong/game.html", context)

@login_required
def game_client(request, game_id):
    match = Match.objects.get(id=game_id)
    if not match:
        return redirect("lobby-home")
    if not match.is_in_match(request.user):
        return redirect("lobby-home")
    return render(request, "pong/game_client.html")