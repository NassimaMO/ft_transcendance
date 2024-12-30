from rest_framework import status # type: ignore
from rest_framework.response import Response # type: ignore
from asgiref.sync import async_to_sync # type: ignore
from channels.layers import get_channel_layer # type: ignore
from account.models import User, UserChange
from matchmaker.models import LobbyChange, LobbyPlayer
import logging

logger = logging.getLogger('default')


def check_user(**kwargs):
    """Helper to centralize user checking"""

    user_id = kwargs.get("user_id")
    username = kwargs.get("username")
    request_status = status.HTTP_404_NOT_FOUND
    user_message = ''
    error = ''
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except Exception:
            user = None
        user_message = f"with id {user_id}"
    elif username:
        try:
            user = User.objects.get(username=username)
        except Exception:
            user = None
        user_message = f"with username {username}"
    else:
        user = None
        error = ": Missing or invalid identifier"
        request_status = status.HTTP_400_BAD_REQUEST
    if not user:
        message = {
            "errors": {
                "unknown_user": f"User {user_message} not found {error}"
                }
            }
        return {"user": None, "error_response": Response(message, status=request_status)}
    return {"user": user, "user_message": user_message}


def send_ws_message(recipient_type, recipient_id, message_type, **extra) :
    """Helper to send messages to channels"""
    message = {
            "type": message_type,
            **extra
        }
    group_name = f"{recipient_type}_{recipient_id}"
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        message
    )
    logger.info(f"[API] Sending message to channel : {group_name} : {message}")


def send_notifications(recipient_type, recipient_id, *changes):
    """Helper to send api notifications to channels"""

    send_ws_message(recipient_type, recipient_id, "api_notif", changes=changes)


def change_lobby_api(player, lobby):
    send_notifications("lobby", player.lobby.id, {'type': LobbyChange.LEAVE, 'username': player.user.username})
    new_leader = player.change_lobby(lobby)
    if new_leader:
        send_notifications("lobby_player", new_leader.id, {'type': LobbyChange.PLAYER})
    send_notifications("lobby", lobby.id, {'type': LobbyChange.JOIN, 'username': player.user.username})
    send_notifications("lobby_player", player.id, {'type': LobbyChange.LOBBY})

def leave_lobby_api(player, back_to_main_lobby=True):
    send_notifications("lobby", player.lobby.id, {'type': LobbyChange.LEAVE, 'username': player.user.username})
    new_leader = player.leave_lobby()
    if new_leader:
        send_notifications("lobby_player", new_leader.id, {'type': LobbyChange.PLAYER})
    if back_to_main_lobby:
        player.join_lobby()
        send_notifications("lobby_player", player.id, {'type': LobbyChange.LOBBY})

def notify_friends_api(user):
    for friend in user.friends.all():
        friend_player = LobbyPlayer.get_by_user(friend)
        if friend_player:
            send_notifications("lobby_player", friend_player.id, {'type': UserChange.INFO, 'username': user.username})