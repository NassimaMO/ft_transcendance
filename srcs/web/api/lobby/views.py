from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.models import User
from matchmaker.serializers import MatchChoiceSerializer
from matchmaker.models import Lobby, LobbyPlayer, LobbyRequest
from matchmaker.serializers import LobbySerializer, LobbyPlayerSerializer, LobbyRequestSerializer
from api.utils import check_user, send_notifications, send_ws_message
import logging

logger = logging.getLogger("default")

MATCH_CHOICE_CHANGE = "match-choice"
LEAVE_CHANGE = "leave"
JOIN_CHANGE = "join"
LOBBY_REQUEST_CHANGE = "lobby-request"
LOBBY_CHANGE = "lobby"
MATCHMAKING_CHANGE = "matchmaking"
PLAYER_CHANGE = "player"

class UserLobbiesMainView(APIView):
    """URL users/me/lobbies/main"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request):
        """Get your Lobby"""

        try:
            lobby = Lobby.get_by_user(request.user)
            if lobby:
                message = {
                    "lobby": LobbySerializer(lobby, context={"request": request}).data
                }
                return Response(message, status=status.HTTP_200_OK)
            return Response({"message": "You are not in a lobby."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error fetching lobby: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Create your Lobby"""

        try:
            lobby = Lobby.get_by_user(request.user)
            if not lobby:
                lobby = Lobby.get_or_create(request.user)
                request_status = status.HTTP_201_CREATED
            else:
                request_status = status.HTTP_200_OK
            message = {
                "lobby_id": lobby.id
            }
            return Response(message, status=request_status)
        except Exception as e:
            logger.error(f"Error creating lobby: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        """Change your Lobby (match choice, queue, open/public)"""

        try:
            lobby = Lobby.get_by_user(request.user)
            if not lobby:
                return Response({"errors": {"no_lobby": "You are not in a lobby."}}, status=status.HTTP_400_BAD_REQUEST)
            if not lobby.is_leader(request.user):
                return Response({"errors": {"no_leader": "You are not the lobby leader."}}, status=status.HTTP_403_FORBIDDEN)
            is_in_queue = request.data.get("is_in_queue")
            match_choice = request.data.get("match-choice")
            if match_choice:
                serializer = MatchChoiceSerializer(data=match_choice)
                if serializer.is_valid():
                    match_choice_instance = serializer.save()
                    lobby.match_choice = match_choice_instance
                    lobby.save()
                    logger.info(f"[API] Match choice patch request data: {match_choice}")
                    logger.info(f"[API] Match choice deserialized: {MatchChoiceSerializer(instance=match_choice_instance).data}")
                    send_notifications("lobby", lobby.id, {'type':MATCH_CHOICE_CHANGE})
                    return Response(
                        {
                            "match_choice_id": match_choice_instance.id,
                            "need_matchmaking": match_choice_instance.need_matchmaking(),
                        },
                        status=status.HTTP_200_OK)
                else:
                    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            elif is_in_queue is not None:
                if is_in_queue == True:
                    if lobby.is_in_queue:
                        return Response({"errors": {"is_in_queue": "You are already in queue."}},
                                        status=status.HTTP_400_BAD_REQUEST)
                    lobby.is_in_queue = True
                    lobby.save()
                    send_notifications("lobby", lobby.id, {'type':MATCHMAKING_CHANGE})
                    send_ws_message("matchmaking_user", request.user.id, "start")
                    return Response({"message": "Matchmaking started."}, status=status.HTTP_200_OK)
                elif is_in_queue == False:
                    if not lobby.is_in_queue:
                        return Response({"errors": {"is_in_queue": "You are not in queue."}}, status=status.HTTP_400_BAD_REQUEST)
                    lobby.is_in_queue = False
                    lobby.save()
                    send_notifications("lobby", lobby.id, {'type':MATCHMAKING_CHANGE})
                    send_ws_message("matchmaking_user", request.user.id, "disconnect")
                    return Response({"message": "Matchmaking stopped."}, status=status.HTTP_200_OK)
                else:
                    return Response({"errors": {"is_in_queue": "Invalid value for 'is_in_queue'. Expected true or false."}}, 
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"errors": {"invalid_request": "No valid data provided."}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error modifying lobby: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """Leave your Lobby"""

        try:
            lobby_player = LobbyPlayer.get_by_user(request.user)
            if not lobby_player:
                return Response({"errors": {"no_lobby": "You are not in a lobby."}}, status=status.HTTP_400_BAD_REQUEST)
            lobby_id = lobby_player.lobby.id
            lobby_player.leave_lobby()
            send_notifications( "lobby", lobby_id, {'type':LEAVE_CHANGE, "username": request.user.username})
            return Response({"message": "You left the lobby."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error leaving lobby: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLobbiesMainRequestsView(APIView):
    """URL users/me/lobbies/main/requests"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request):
        """Get your Lobby's Requests"""
    
        try:
            lobby_player = LobbyPlayer.get_by_user(request.user)
            if not lobby_player:
                return Response({"errors": {"no_lobby": "You are not in a lobby."}}, status=status.HTTP_400_BAD_REQUEST)
            requests = LobbyPlayerSerializer(lobby_player, context={"request": request}).data.get("requests", [])
            return Response({"requests": requests}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching lobby requests: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLobbiesMainRequestView(APIView):
    """URL users/me/lobbies/main/requests/<int/str:user_id_or_username>"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def delete(self, request, **kwargs):
        """Reject a Lobby Request"""

        try:
            user_checking = check_user(**kwargs)
            user = user_checking.get("user")
            if not user:
                return user_checking.get("error_response")
            lobby_player = LobbyPlayer.get_by_user(request.user)
            if not lobby_player:
                return Response({"errors": {"no_lobby": "You are not in a lobby."}}, status=status.HTTP_400_BAD_REQUEST)
            request_type = request.data.get('type')
            if not request_type:
                return Response({"errors": {"type": "Missing request type. Expected values : 'join' or 'invite'."}}, 
                                status=status.HTTP_400_BAD_REQUEST)
            lobby_request = lobby_player.get_request(user.username, request_type)
            if not lobby_request:
                return Response({"errors": {"unknown_request": "This request was not found."}}, status=status.HTTP_404_NOT_FOUND)
            lobby_request.delete()
            send_notifications("lobby_player", lobby_player.id, {'type':LOBBY_REQUEST_CHANGE})
            return Response({"message": "Request rejected."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error rejecting lobby request: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, **kwargs):
        """Accept a Lobby Request"""

        try:
            user_checking = check_user(**kwargs)
            user = user_checking.get("user")
            if not user:
                return user_checking.get("error_response")
            lobby_player = LobbyPlayer.get_by_user(request.user)
            if not lobby_player:
                return Response({"errors": {"no_lobby": "You are not in a lobby."}}, status=status.HTTP_400_BAD_REQUEST)
            request_type = request.data.get('type')
            if not request_type:
                return Response({"errors": {"type": "Missing request type. Expected values : 'join' or 'invite'."}}, 
                                status=status.HTTP_400_BAD_REQUEST)
            lobby_request = lobby_player.get_request(user.username, request_type)
            if not lobby_request:
                return Response({"errors": {"unknown_request": "This request was not found."}}, status=status.HTTP_404_NOT_FOUND)
            sender_player = LobbyPlayer.get_by_user(user)
            if not sender_player:
                return Response({"errors": {"invalid_request": "This request is no longer valid."}}, status=status.HTTP_400_BAD_REQUEST)
            request_data = LobbyRequestSerializer(lobby_request).data
            if request_data['type'] == "invite":
                lobby_player.change_lobby(sender_player.lobby)
                send_notifications("lobby", sender_player.lobby.id, {'type':JOIN_CHANGE})
                send_notifications("lobby_player", lobby_player.id, {'type':LOBBY_CHANGE})
            elif request_data['type'] == "join":
                sender_player.change_lobby(lobby_player.lobby)
                send_notifications("lobby", lobby_player.lobby.id, {'type':JOIN_CHANGE})
                send_notifications("lobby_player", sender_player.id, {'type':LOBBY_CHANGE})
            lobby_request.delete()
            send_notifications("lobby_player", lobby_player.id, {'type':LOBBY_REQUEST_CHANGE})
            return Response({"message": "Request accepted."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error accepting lobby request: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLobbiesMainMembersView(APIView):
    """URL users/me/lobbies/main/members"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request):
        """Get your Lobby's Members"""

        try:
            lobby_player = LobbyPlayer.get_by_user(request.user)
            if not lobby_player:
                return Response({"errors": {"no_lobby": "You are not in a lobby."}}, status=status.HTTP_400_BAD_REQUEST)
            members = LobbyPlayerSerializer(lobby_player, context={"request": request}).data.get("members", [])
            return Response({"members": members}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching lobby members: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLobbiesMainMemberView(APIView):
    """URL users/me/lobbies/main/members/<int:member_id>"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def delete(self, request, member_id):
        """Kick a Member of your Lobby"""

        try:
            lobby_player = LobbyPlayer.get_by_user(request.user)
            member = LobbyPlayer.get_by(id=member_id)
            if not lobby_player:
                return Response({"errors": {"no_lobby": "You are not in a lobby."}}, status=status.HTTP_400_BAD_REQUEST)
            if not member:
                return Response({"errors": {"unknown_user": "This member does not exist."}}, status=status.HTTP_404_NOT_FOUND)
            member.change_lobby()
            send_notifications("lobby_player", lobby_player.id, {'type':LEAVE_CHANGE, "username": member.username})
            return Response({"message": f"Member '{member.username}' has been removed."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error removing lobby member: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserLobbiesView(APIView):
    """URL users/me/lobbies"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request):
        """Get available Lobbies"""


class UserLobbyView(APIView):
    """URL users/me/lobbies/<int:lobby_id>"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def post(self, request, lobby_id):
        """Join an open Lobby"""


class UserLobbyRequestsView(APIView):
    """URL users/me/lobbies/<int:lobby_id>/requests"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def post(self, request, lobby_id):
        """Send a Request to a Lobby"""


class UserFriendLobbyRequests(APIView):
    """URL users/me/friends/<friend_id_or_username>/lobby/requests"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def post(self, request, **kwargs):
        """Send a Request to a User's Lobby"""

        try:
            message = {'errors':{}}
            user_checking = check_user(**kwargs)
            user = user_checking.get("user")
            if not user:
                return user_checking.get("error_response")
            lobby_player = LobbyPlayer.get_by_user(user) if user else None
            request_type = request.data.get("type")
            if not request_type :
                message["errors"]["type"] = "Missing request type. Expected value: 'invite' or 'join'."
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if request_type not in ['invite', 'join']:
                message["errors"]["type"] = f"Invalid request type : '{request_type}'. Expected value: 'invite' or 'join'."
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if user not in request.user.friends.all():
                message["errors"]["not_a_friend"] = f"Friend {user_checking.get('user_message')} not found. Is it your imaginary friend ?"
                return Response(message, status=status.HTTP_404_NOT_FOUND)
            if user not in request.user.friends.all() and (not lobby_player or not lobby_player.lobby.is_public):
                message["errors"]["not_allowed"] = "You do not have right to access this lobby."
                return Response(message, status=status.HTTP_403_FORBIDDEN)
            elif not lobby_player:
                message["errors"]["no_lobby"] = "This lobby does not exist."
                return Response(message, status=status.HTTP_404_NOT_FOUND)
            request = LobbyRequest(recipient=lobby_player, sender=request.user.username, type=request_type)
            request.save()
            send_notifications('lobby_player', lobby_player.id, {'type':LOBBY_REQUEST_CHANGE})
            return Response(message, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error sending lobby request: {e}")
            return Response({"errors": {"server_error": "An unexpected error occurred."}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserLobbiesMainMembersMeView(APIView):
    """URL users/me/lobbies/main/members/me"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def put(self, request):
        """CHANGE ALL your player info"""

        lobby_player = LobbyPlayer.get_by_user(request.user)
        message = {'errors':{}}
        if not lobby_player:
            message["errors"]["no_lobby"] = "You are not in a lobby."
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        serializer = LobbyPlayerSerializer(lobby_player, data=request.data, context={"request": request})
        if serializer.is_valid():
            lobby_player = serializer.save()
            send_notifications("lobby", lobby_player.lobby.id, {'type':PLAYER_CHANGE})
            return Response({"message": "Player info updated successfully."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """CHANGE SOME of your player info"""

        lobby_player = LobbyPlayer.get_by_user(request.user)
        message = {'errors':{}}
        if not lobby_player:
            message["errors"]["no_lobby"] = "You are not in a lobby."
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        serializer = LobbyPlayerSerializer(lobby_player, data=request.data, context={"request": request}, partial=True)
        if serializer.is_valid():
            lobby_player = serializer.save()
            logger.info(f"LobbyPlayer updated: {LobbyPlayerSerializer(lobby_player).data}")
            send_notifications("lobby", lobby_player.lobby.id, {'type': PLAYER_CHANGE})
            return Response({"message": "Player info partially updated."}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)