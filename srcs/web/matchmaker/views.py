import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from matchmaker.forms import MatchChoiceForm
from .models import Lobby, LobbyPlayer
from .serializers import LobbySerializer, LobbyPlayerSerializer
from account.serializers import UserSerializer
from account.models import Status
from django.utils import timezone


logger = logging.getLogger('default')

@login_required
def lobby_home_view(request):
    lobby = Lobby.get_or_create(request.user)
    return redirect("lobby", lobby.id)

@login_required
def modes_view(request):
    lobby = Lobby.get_by_user(request.user)
    if not lobby :
        return redirect("lobby-home")
    if request.method == 'POST' :
        mode_form = MatchChoiceForm(data=request.POST, instance=lobby.match_choice)
        if mode_form.is_valid():
            lobby.match_choice = mode_form.save()
            lobby.save()
        else:
            return render(request, 'matchmaker/modes.html', 
                          {'mode_form': mode_form, 'lobby_player': lobby_player, 'form_errors': mode_form.errors})
    else :
        mode_form = MatchChoiceForm(instance=lobby.match_choice)
    lobby_player = LobbyPlayer.get_or_create(request.user)
    data = LobbyPlayerSerializer(lobby_player, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/modes.html', {'mode_form': mode_form, 'lobby_player': data})

@login_required
def lobby_list_view(request) :
    lobby = Lobby.get_by_user(request.user)
    if not lobby :
        return redirect("lobby-home")
    lobby_data = LobbySerializer(lobby, context={'request':request, 'type':'template'}).data
    lobby_users = [lobby_player['user'] for lobby_player in lobby_data['members']]
    return render(request, 'matchmaker/lobby_list.html', 
                  {'lobby_players': lobby_data['members'], 
                    'lobby_users': lobby_users, 
                    'user': lobby_users[0], 
                    'Status': Status})

@login_required
def friends_list_view(request) :
    user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/friends_list.html', {'user': user, 'Status': Status})

@login_required
def matchmaking_view(request) :
    lobby_player = LobbyPlayer.get_or_create(request.user)
    if not lobby_player or not lobby_player.lobby:
        return redirect("lobby-home")
    lobby_player_data = LobbyPlayerSerializer(lobby_player, context={'request':request, 'type':'template'}).data
    lobby_data = LobbySerializer(lobby_player.lobby, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/matchmaking.html', {'lobby_player': lobby_player_data, 'lobby': lobby_data})

@login_required
def invite_banner_view(request) :
    user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/invite_banner.html', {'friends': user['friends']})

@login_required
def lobby_requests_view(request) :
    lobby_player = LobbyPlayer.get_or_create(request.user)
    if not lobby_player or not lobby_player.lobby:
        return redirect("lobby-home")
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
    lobby_data = LobbySerializer(lobby, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/lobby_players.html', {'lobby_players': lobby_data['members']})

@login_required
def lobby_view(request, lobby_id) :
    player = LobbyPlayer.get_by_user(request.user)
    if not player or not player.lobby:
        return redirect("lobby-home")
    if request.method == 'POST' :
        mode_form = MatchChoiceForm(data=request.POST, instance=player.lobby.match_choice)
        mode_form.save()
    else :
        mode_form = MatchChoiceForm(instance=player.lobby.match_choice)
        lobby = LobbySerializer(player.lobby, context={'request':request, 'type':'template'}).data
        user = UserSerializer(request.user, context={'request':request, 'type':'template'}).data
    return render(request, 'matchmaker/lobby.html', 
                  {"lobby": lobby, 
                   'lobby_users': [lobby_player['user'] for lobby_player in lobby['members']], 
                   'mode_form': mode_form, 'user': user, 'Status': Status, "timestamp": int(timezone.now().timestamp())})
