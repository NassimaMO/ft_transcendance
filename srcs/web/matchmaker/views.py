from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger('default')

@login_required
def matchmaking_view(request, match_choice_id):
    return render(request, 'matchmaker/matchmaking.html', {"match_choice_id": match_choice_id})