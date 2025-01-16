from rest_framework import status # type: ignore
from rest_framework.response import Response # type: ignore
from asgiref.sync import async_to_sync # type: ignore
from channels.layers import get_channel_layer # type: ignore
from account.models import User, UserChange
from matchmaker.models import LobbyChange, LobbyPlayer
import logging

logger = logging.getLogger('default')

def get_message_str(code: str, level: str, **kwargs) -> str :
    """Helper to get an api str error for an error code"""

    if code == "server_error":
        return "An unexpected error occurred."
    if code == "no_available_lobby":
        return "There is no available lobby."
    if code == "no_requests":
        return "You have no requests."
    if code == "not_in_lobby":
        return "You are not in a lobby."
    if code == "not_same_lobby":
        return f"You and '{kwargs.get('username')}' are not in the same lobby."
    if code == "no_player" :
        return "This user is not in a lobby."
    if code == "forbidden_lobby" :
        return "You are not allowed to access this lobby."
    if code == "not_leader":
        return "You are not the lobby leader."
    if code == "missing_request_type":
        return "Missing request type. Expected value: 'invite' or 'join'."
    if code == "invalid_request_type" :
        return f"Invalid request type : '{kwargs.get('request_type')}'. Expected values: 'invite' or 'join'."
    if code == "invalid_is_in_queue":
        return f"Invalid value for 'is_in_queue': '{kwargs.get('is_in_queue')}'. Expected values: 'true' or 'false'."
    if code == "already_in_queue":
        return "You are already in queue."
    if code == "not_in_queue":
        return "You are not in queue."
    if code == "matchmaking_start":
        return "Matchmaking successfully started."
    if code == "matchmaking_stop":
        return "Matchmaking successfully stopped."
    if code == "info_change":
        return "Player info updated successfully."
    if code == "no_data":
        return "No data provided."
    if code == "leave_lobby":
        return "You left the lobby."
    if code == "reject_request":
        return f"{kwargs.get('request_type').capitalize()} request from {kwargs.get('sender')} rejected."
    if code == "accept_request":
        return f"{kwargs.get('request_type').capitalize()} request from {kwargs.get('sender')} accepted."
    if code == "send_request":
        return f"{kwargs.get('request_type').capitalize()} request sent to {kwargs.get('recipient')}."
    if code == "kick_member":
        return f"Member '{kwargs.get('username')}' has been kicked."
    if code[:8] == "unknown":
        return f"This {code[8:]} was not found."


def add_message(message_dict: dict, code: str, level: str = "INFO", **kwargs) -> None :
    """Helper to add an api error to a dict"""

    if level == "ERROR":
        if not message_dict.get("errors"):
            message_dict["errors"] = {}
    elif level == "INFO":
        if not message_dict.get("messages"):
            message_dict["messages"] = {}
    if "request_type" in code:
        message_dict["errors"]["type"] = get_message_str(code, "ERROR", **kwargs)
    else:
        if level == "ERROR":
            message_dict["errors"][code] = get_message_str(code, "ERROR", **kwargs)
        elif level == "INFO":
            message_dict["messages"][code] = get_message_str(code, "ERROR", **kwargs)


def check_user(**kwargs):
    """Helper to centralize user checking on id or username"""

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