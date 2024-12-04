import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from matchmaker.forms import MatchChoiceForm
from .models import Lobby, LobbyPlayer
from .serializers import LobbySerializer, LobbyPlayerSerializer
from account.serializers import UserSerializer


logger = logging.getLogger('default')

@login_required
def lobby_home_view(request):
    lobby_id = Lobby.get_or_create(request.user).id
    return redirect("lobby", lobby_id)

@login_required
def modes_view(request):
    lobby = Lobby.get_by_user(request.user)
    if not lobby :
        return redirect("lobby-home")
    if request.method == 'POST' :
        mode_form = MatchChoiceForm(data=request.POST)
        lobby.match_choice = mode_form.save()
        lobby.save()
    else :
        mode_form = MatchChoiceForm(instance=lobby.match_choice)
    lobby_player = LobbyPlayer.get_or_create(request.user)
    return render(request, 'matchmaker/modes.html', {'mode_form': mode_form, 'lobby_player': lobby_player})

@login_required
def lobby_list_view(request) :
    lobby = Lobby.get_by_user(request.user)
    if not lobby :
        return redirect("lobby-home")
    lobby = LobbySerializer(lobby, context={'request':request, 'type':'template'}).data
    user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/lobby_list.html', 
                  {'lobby_players': lobby['members'], 
                    'lobby_users': [lobby_player['user'] for lobby_player in lobby['members']], 
                    'user': user})

@login_required
def friends_list_view(request) :
    user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/friends_list.html', {'user': user})

@login_required
def invite_banner_view(request) :
    user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/invite_banner.html', {'friends': user['friends']})

@login_required
def lobby_requests_view(request) :
    lobby_player = LobbyPlayer.get_or_create(request.user)
    data = LobbyPlayerSerializer(lobby_player, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/lobby_requests.html', {'requests': data['requests']})

@login_required
def friend_requests_view(request) :
    user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/friend_requests.html', {'requests': user['requests']})

@login_required
def lobby_players_view(request) :
    lobby = Lobby.get_by_user(request.user)
    if not lobby :
        return redirect("lobby-home")
    lobby = LobbySerializer(lobby, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/lobby_players.html', {'lobby_players': lobby['members']})

@login_required
def lobby_view(request, lobby_id) :
    if request.method == 'POST' :
        mode_form = MatchChoiceForm(data=request.POST)
        mode_form.save()
    else :
        mode_form = MatchChoiceForm()
        lobby = Lobby.get_by_user(request.user)
        if not lobby :
            return redirect("lobby-home")
        lobby = LobbySerializer(lobby, context={'request':request, 'type':'template'}).data
        user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/lobby.html', 
                  {"lobby": lobby, 
                   'lobby_users': [lobby_player['user'] for lobby_player in lobby['members']], 
                   'mode_form': mode_form, 'user': user})
