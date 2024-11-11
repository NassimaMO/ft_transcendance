import logging
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from matchmaker.forms import MatchChoiceForm
from .models import Lobby, LobbyPlayer, LobbyRequest
from .serializers import LobbySerializer, LobbyPlayerSerializer
from account.serializers import UserSerializer


logger = logging.getLogger('default')

@login_required
def lobby_home_view(request):
    logger.info(f"{Lobby.query.all()}")
    lobby_id = Lobby.get_or_create(request.user).id
    return redirect("lobby", lobby_id)

@login_required
def lobby_get_request(request, lobby_id):
    if request.method == 'GET' :
        lobby = Lobby.get_by(id=lobby_id)
        if lobby :
            return JsonResponse({"lobby": LobbySerializer(lobby[0], context={'request': request}).data})
    return JsonResponse({}, status=403)

@login_required
def modes_view(request):
    if request.method == 'POST' :
        mode_form = MatchChoiceForm(data=request.POST)
        mode_form.save()
    else :
        mode_form = MatchChoiceForm()
    lobby_player = LobbyPlayer.get_or_create(request.user)
    return render(request, 'matchmaker/modes.html', {'mode_form': mode_form, 'lobby_player': lobby_player})

@login_required
def lobby_list_view(request) :
    lobby = LobbySerializer(Lobby.get_or_create(request.user), context={'request': request}).data
    user = UserSerializer(request.user, context={'request':request}).data
    return render(request, 'matchmaker/lobby_list.html', {'lobby_players': lobby['players'], 'lobby_users': [lobby_player['user'] for lobby_player in lobby['players']], 'user': user})

@login_required
def friends_list_view(request) :
    user = UserSerializer(request.user, context={'request': request}).data
    return render(request, 'matchmaker/friends_list.html', {'user': user})

@login_required
def invite_banner_view(request) :
    user = UserSerializer(request.user, context={'request': request}).data
    return render(request, 'matchmaker/invite_banner.html', {'friends': user['friends']})

@login_required
def lobby_requests_view(request) :
    lobby_player = LobbyPlayer.get_or_create(request.user)
    data = LobbyPlayerSerializer(lobby_player, context={'request': request}).data
    return render(request, 'matchmaker/lobby_requests.html', {'requests': data['requests']})

@login_required
def friend_requests_view(request) :
    user = UserSerializer(request.user, context={'request': request}).data
    return render(request, 'matchmaker/friend_requests.html', {'requests': user['requests']})

@login_required
def lobby_players_view(request) :
    lobby = LobbySerializer(Lobby.get_or_create(request.user), context={'request': request}).data
    return render(request, 'matchmaker/lobby_players.html', {'lobby_players': lobby['players']})

@login_required
def lobby_view(request, lobby_id) :
    if request.method == 'POST' :
        mode_form = MatchChoiceForm(data=request.POST)
        mode_form.save()
    else :
        mode_form = MatchChoiceForm()
        response = lobby_get_request(request, lobby_id)
        if response.get("status") == 403 :
            return redirect("lobby-home")
        lobby = json.loads(response.content.decode('utf-8')).get("lobby", None)
        if not lobby :
            return redirect("lobby-home")
        user = UserSerializer(request.user, context={'request': request}).data
    return render(request, 'matchmaker/lobby.html', {"lobby": lobby, 'lobby_users': [lobby_player['user'] for lobby_player in lobby['players']], 'mode_form': mode_form, 'user': user})
