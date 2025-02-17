from rest_framework import status # type: ignore
from rest_framework.response import Response # type: ignore
from asgiref.sync import async_to_sync # type: ignore
from channels.layers import get_channel_layer # type: ignore
from account.models import User, UserChange
from matchmaker.models import LobbyChange, LobbyPlayer, LobbyStatus, GameMode, Team, Entry, Match
import logging
import random

logger = logging.getLogger('default')


def get_message_str(code: str, level: str, **kwargs) -> str :
    """Helper to get an api str error for an error code"""

    if code == "server_error":
        return "An unexpected error occurred."
    #
    if code == "no_available_lobby":
        return "There is no available lobby."
    #
    if code == "no_friend":
        return "You have no friend... :'("
    #
    if code == "no_friend_request":
        return "No friend request. Be nicer, it will come."
    #
    if code == "no_player" :
        return "This user is not in a lobby."
    #
    if code == "not_in_lobby":
        return "You are not in a lobby."
    #
    if code == "not_same_lobby":
        return f"You and '{kwargs.get('username')}' are not in the same lobby."
    #
    if code == "forbidden_lobby" :
        return "You are not allowed to access this lobby."
    #
    if code == "not_leader":
        return "You are not the lobby leader."
    #
    if code == "missing_request_type":
        return "Missing request type. Expected value: 'invite' or 'join'."
    #
    if code == "invalid_request_type" :
        return f"Invalid request type : '{kwargs.get('request_type')}'. Expected values: 'invite' or 'join'."
    #
    if code == "invalid_lobby_status":
        return "Invalid lobby status : expected 'default' or 'start'."
    #
    if code == "already_in_queue":
        return "You are already in queue."
    #
    if code == "not_in_queue":
        return "You are not in queue."
    #
    if code == "matchmaking_started":
        return "Matchmaking successfully started."
    #
    if code == "matchmaking_stopped":
        return "Matchmaking successfully stopped."
    #
    if code == "info_updated":
        return "Player info updated successfully."
    #
    if code == "no_data":
        return "No data provided."
    #
    if code == "lobby_leave":
        return "You left the lobby."
    #
    if code == "request_denied":
        return f"{kwargs.get('request_type').capitalize()} request from user {kwargs.get('str')} denied."
    #
    if code == "request_accepted":
        return f"{kwargs.get('request_type').capitalize()} request from user {kwargs.get('str')} accepted."
    #
    if code == "request_sent":
        return f"{kwargs.get('request_type').capitalize()} request sent to user {kwargs.get('str')}."
    #
    if code == "member_kicked":
        return f"Member '{kwargs.get('username')}' has been kicked."
    #
    if code == "unknown_friend_request":
        return f"Request from user {kwargs.get('str')} not found. Is it your imaginary friend ?"
    #
    if code == "unknown_friend":
        return f"User {kwargs.get('str')} not found. Is it your imaginary friend ?"
    #
    if code == "friend_requests_removed":
        return "All friend requests removed."
    #
    if code == "self_friend_attempt":
        return f"You cannot add yourself as a friend. This is sad btw. Seek help."
    #
    if code == "already_friend":
        return f"No need to send a friend request, you two are already friends. I know, it's unbelievable."
    #
    if code == "already_sent":
        return f"You already asked this user to be your friend. Stop insist. You need to face the truth."
    #
    if code == "friend_request_sent":
        return f"A friend request has been sent to user {kwargs.get('str')}"
    #
    if code == "friend_request_accepted":
        return f"Friend request from user {kwargs.get('str')} successfully accepted. You two are now friends."
    #
    if code == "friend_request_denied":
        return f"Friend request from user {kwargs.get('str')} successfully denied."
    #
    if code == "registration_success":
        return "You registered successfully."
    #
    if code == "friend_removed":
        return f"User {kwargs.get('str')} is no longer your friend. Good riddance."
    #
    split = code.split('_')
    if split[-1] == "updated":
        return f"{' '.join([s.capitalize() if i == 0 else s for i, s in enumerate(split[:-1])])} info updated successfully."
    #
    if split[-1] == "deleted":
        return f"{' '.join([s.capitalize() if i == 0 else s for i, s in enumerate(split[:-1])])} deleted successfully."
    #
    if split[-1] == "created":
        return f"A {' '.join([s.capitalize() if i == 0 else s for i, s in enumerate(split[:-1])])} has been successfully created."
    #
    if split[0] == "unknown":
        return f"This {' '.join([s for s in split[1:]])} was not found."
    #
    if split[0] == "no":
        return f"There is no {' '.join([s for s in split[1:]])}."
    #
    return "Invalid request (error code unknown)"


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


def check_args(_class, **kwargs):
    """Helper to centralize objects checking on id or username"""

    id = None
    name = None
    for key, value in kwargs.items():
        if key == f"{_class.__name__.lower()}_id":
            id = value
        elif key == f"{_class.__name__.lower()}_name" or key == f"{_class.__name__.lower()}name":
            name = value
    if id is None and name is None:
        return {"obj": None, "error_response": Response({}, status=status.HTTP_400_BAD_REQUEST)}
    request_status = status.HTTP_404_NOT_FOUND
    str = ''
    error = ''
    if id:
        try:
            obj = _class.objects.get(id=id)
        except Exception:
            obj = None
        str = f"with id {id}"
    elif name:
        try:
            if _class == User:
                obj = _class.objects.get(username=name)
            else:
                obj = _class.objects.get(name=name)
        except Exception:
            obj = None
        str = f"with name {name}"
    else:
        obj = None
        error = ": Missing or invalid identifier"
        request_status = status.HTTP_400_BAD_REQUEST
    if not obj:
        message = {
            "errors": {
                f"unknown_{_class.__name__.lower()}": f"{_class.__name__} {str} not found {error}"
                }
            }
        return {"obj": None, "error_response": Response(message, status=request_status)}
    return {"obj": obj, "str": str}


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
    logger.info(f"[API] Sending {message_type} to channel {group_name} - Changes : {[change.get('type', change) for change in extra.get('changes', {})]}")


def send_notifications(recipient_type, recipient_id, *changes):
    """Helper to send api notifications to channels"""

    send_ws_message(recipient_type, recipient_id, "api_notif", changes=changes)


def change_lobby_api(player, lobby):
    send_notifications("lobby", player.lobby.id, {'type': LobbyChange.LEAVE, 'username': player.user.username})
    send_notifications("matchmaking_lobby", player.lobby.id, {'type': LobbyChange.LEAVE})
    new_leader = player.change_lobby(lobby)
    if new_leader:
        send_notifications("lobby_player", new_leader.id, {'type': LobbyChange.PLAYER})
    send_notifications("lobby", lobby.id, {'type': LobbyChange.JOIN, 'username': player.user.username})
    send_notifications("lobby_player", player.id, {'type': LobbyChange.LOBBY})
    send_notifications("matchmaking_player", player.id, {'type': LobbyChange.LOBBY})


def change_matchmaking_api(lobby_player, change):
    lobby_player.lobby.status = LobbyStatus.IN_QUEUE if change == "start" else LobbyStatus.DEFAULT
    lobby_player.lobby.save()
    send_ws_message("matchmaking_player", lobby_player.id, change)


def leave_lobby_api(player, back_to_main_lobby=True):
    send_notifications("lobby", player.lobby.id, {'type': LobbyChange.LEAVE, 'username': player.user.username})
    send_notifications("matchmaking_lobby", player.lobby.id, {'type': LobbyChange.LEAVE})
    if player.lobby.status == LobbyStatus.IN_QUEUE:
        change_matchmaking_api(player, "stop")
    new_leader = player.leave_lobby()
    if new_leader:
        send_notifications("lobby_player", new_leader.id, {'type': LobbyChange.PLAYER})
    if back_to_main_lobby:
        player.join_lobby()
        send_notifications("lobby_player", player.id, {'type': LobbyChange.LOBBY})
        send_notifications("matchmaking_player", player.id, {'type': LobbyChange.LOBBY})


def notify_friends_api(user):
    for friend in user.friends.all():
        friend_player = LobbyPlayer.get_by_user(friend)
        if friend_player:
            send_notifications("lobby_player", friend_player.id, {'type': UserChange.INFO, 'username': user.username})


def create_match(teams):
    match_choice = teams[0][0].match_choice
    match = Match.objects.create(info=match_choice)
    for team in teams:
        team_obj = Team.objects.create()
        for lobby in team:
            team_obj.players.add(*[Entry.objects.create(user=player.user, pseudo=player.pseudo) for player in lobby.members])
        match.teams.add(team_obj)
    if match_choice.mode == GameMode.SOLO:
        team_obj = Team.objects.create()
        team_obj.players.add(Entry.objects.create(user=None, pseudo="IA"))
        match.teams.add(team_obj)
    return match