from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from account.models import User
import logging
import json

logger = logging.getLogger('default')


@login_required
def matchmaking_view(request, match_choice_id):
    return render(request, 'matchmaker/matchmaking.html', {"match_choice_id": match_choice_id})


@login_required
def lobby_view(request):
    return render(request, 'matchmaker/lobby.html') 

