from rest_framework import status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.authentication import SessionAuthentication # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from matchmaker.serializers import MatchChoiceSerializer
from matchmaker.models import Lobby, LobbyPlayer, LobbyRequest, LobbyChange
from matchmaker.serializers import LobbySerializer, LobbyPlayerSerializer, LobbyRequestSerializer
from api.utils import add_message, check_user, send_notifications, change_lobby_api, leave_lobby_api, change_matchmaking_api
import logging

logger = logging.getLogger("default")


class LobbiesView(APIView):
	"""URL lobbies/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""Get available Lobbies"""

		message = {}
		try:
			lobbies = Lobby.query.all()
			available_lobbies = []
			for lobby in lobbies:
				if lobby.is_allowed_for(request.user) :
					available_lobbies.append(LobbySerializer(instance=lobby, context={'request':request}).data)
			if available_lobbies:
				message["lobbies"] = available_lobbies
				return Response(message, status=status.HTTP_200_OK)
			add_message(message, "no_lobby_available")
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			logger.error(f"Error fetching available lobbies: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LobbyView(APIView):
	"""URL lobbies/<int:lobby_id>/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, lobby_id):
		"""Get a Lobby info"""

		message = {}
		try:
			lobby = Lobby.get(lobby_id)
			if not lobby:
				add_message(message, "no_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			lobby_data = LobbySerializer(instance=lobby, context={'request':request}).data
			message["lobby"] = lobby_data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching lobby {lobby_id}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LobbyMembersView(APIView):
	"""URL lobbies/<int:lobby_id>/members/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, lobby_id):
		"""Get Lobby Members"""

		message = {}
		try:
			lobby = Lobby.get(lobby_id)
			if not lobby:
				add_message(message, "no_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			lobby_data = LobbySerializer(instance=lobby, context={'request':request}).data
			members = lobby_data.get('members', [])
			if members:
				message["members"] = members
				return Response(message, status=status.HTTP_200_OK)
			add_message(message, "no_members")
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			logger.error(f"Error fetching lobby {lobby_id} members: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MainLobbyView(APIView):
	"""URL lobbies/main/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""Get your Lobby"""

		message = {}
		try:
			lobby = Lobby.get_by_user(request.user)
			if lobby:
				message["lobby"] = LobbySerializer(lobby, context={"request": request}).data
				return Response(message, status=status.HTTP_200_OK)
			add_message(message, "not_in_lobby")
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			logger.error(f"Error fetching main lobby: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def post(self, request):
		"""Create your Lobby"""

		message = {}
		try:
			lobby = Lobby.get_by_user(request.user)
			if not lobby:
				lobby = Lobby.get_or_create(request.user)
				request_status = status.HTTP_201_CREATED
			else:
				request_status = status.HTTP_200_OK
			message["lobby"] = LobbySerializer(lobby, context={"request": request}).data
			return Response(message, status=request_status)
		except Exception as e:
			logger.error(f"Error creating lobby: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def patch(self, request):
		"""Change your Lobby (match choice, queue, open/public)"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_by_user(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			if not lobby_player.is_leader:
				add_message(message, "not_leader", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			is_in_queue = request.data.get("is_in_queue")
			match_choice = request.data.get("match-choice")
			if match_choice:
				logger.info(match_choice)
				serializer = MatchChoiceSerializer(data=match_choice)
				if serializer.is_valid():
					match_choice_instance = serializer.save()
					lobby_player.lobby.match_choice = match_choice_instance
					lobby_player.lobby.save()
					send_notifications("lobby", lobby_player.lobby.id, {'type': LobbyChange.MATCH_CHOICE})
					message['match_choice'] = {
						'id': match_choice_instance.id,
					}
					add_message(message, "match_choice_updated")
					return Response(message, status=status.HTTP_200_OK)
				else:
					return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
			elif is_in_queue is not None:
				if is_in_queue == True:
					if lobby_player.lobby.is_in_queue:
						add_message(message, "already_in_queue")
						return Response(message, status=status.HTTP_200_OK)
					change_matchmaking_api(lobby_player, "start")
					add_message(message, "matchmaking_started")
					return Response(message, status=status.HTTP_200_OK)
				elif is_in_queue == False:
					if not lobby_player.lobby.is_in_queue:
						add_message(message, "not_in_queue")
						return Response(message, status=status.HTTP_200_OK)
					change_matchmaking_api(lobby_player, "stop")
					add_message(message, "matchmaking_stopped")
					return Response(message, status=status.HTTP_200_OK)
				else:
					add_message(message, "invalid_is_in_queue", level="ERROR")
					return Response(message, status=status.HTTP_400_BAD_REQUEST)
			else:
				add_message(message, "no_data", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.error(f"Error updating lobby: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def put(self, request):
		"""Leave your Lobby (and return to another)"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_by_user(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			leave_lobby_api(lobby_player)
			add_message(message, "lobby_leave")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error leaving lobby: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request):
		"""Leave your Lobby (and don't return to another)"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_by_user(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			leave_lobby_api(lobby_player, back_to_main_lobby=False)
			add_message(message, "lobby_leave")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error leaving lobby: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MainLobbyMembersView(APIView):
	"""URL lobbies/main/members/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""Get your Lobby's Members"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_by_user(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			lobby_data = LobbyPlayerSerializer(lobby_player, context={"request": request}).data
			members = lobby_data.get("members", [])
			if members:
				message["members"] = members
				return Response(message, status=status.HTTP_200_OK)
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			logger.error(f"Error fetching main lobby members: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MainLobbyMemberView(APIView):
	"""URL lobbies/main/members/<int/str:user_id_or_username>/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, **kwargs):
		"""Get a Member info"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			lobby_player = LobbyPlayer.get_by_user(user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "no_player", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			player_data = LobbyPlayerSerializer(lobby_player, context={'request':request}).data
			message['member'] = player_data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching member {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request, **kwargs):
		"""Kick a Player from his lobby"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			lobby_player = LobbyPlayer.get_by_user(request.user)
			player = LobbyPlayer.get_by_user(user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			if not player:
				add_message(message, "no_player", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if player not in lobby_player.lobby.members.all():
				add_message(message, "not_same_lobby", level="ERROR", username=player.user.username)
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if not lobby_player.is_leader:
				add_message(message, "not_leader", level="ERROR", username=player.user.username)
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			leave_lobby_api(player)
			add_message(message, "member_kicked", username=player.user.username)
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error kicking lobby member {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlayerView(APIView):
	"""URL players/<int/str:user_id_or_username>/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, **kwargs):
		"""Get a Player info"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			lobby_player = LobbyPlayer.get_by_user(user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "no_player", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			player_data = LobbyPlayerSerializer(lobby_player, context={'request':request}).data
			message['player'] = player_data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching player {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlayerLobbyView(APIView):
	"""URL players/<int/str:user_id_or_username>/lobby/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, **kwargs):
		"""Get a Player's lobby"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			lobby = Lobby.get_by_user(user)
			if not lobby:
				add_message(message, "no_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if not lobby.is_allowed_for(request.user):
				add_message(message, "forbidden_lobby", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			message['lobby'] = {
				'id': lobby.id,
				'url': f"/api/lobbies/{lobby.id}/"
			}
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching player {user_checking.get('user_message')} lobby: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlayerRequestsView(APIView):
	"""URL players/<int/str:user_id_or_username>/requests/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def post(self, request, **kwargs):
		"""Send a Request to a User's Lobby"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			lobby_player = LobbyPlayer.get_by_user(user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "no_player", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			request_type = request.data.get("type")
			if not request_type :
				add_message(message, "missing_request_type", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			if request_type not in ['invite', 'join']:
				add_message(message, "invalid_request_type", level="ERROR", request_type=request_type)
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			if not lobby_player.lobby.is_allowed_for(request.user):
				add_message(message, "forbidden_lobby", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			lobby_request = LobbyRequest(recipient=lobby_player, _sender=request.user.username, _type=request_type)
			lobby_request.save()
			send_notifications('lobby_player', lobby_player.id, {'type':LobbyChange.LOBBY_REQUEST})
			add_message(message, "request_sent", request_type=request_type, recipient=user.username)
			return Response(message, status=status.HTTP_201_CREATED)
		except Exception as e:
			logger.error(f"Error sending lobby request: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlayerMeView(APIView):
	"""URL players/me/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def put(self, request):
		"""CHANGE ALL your player info"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_by_user(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			serializer = LobbyPlayerSerializer(lobby_player, data=request.data, context={"request": request})
			if serializer.is_valid():
				lobby_player = serializer.save()
				send_notifications("lobby", lobby_player.lobby.id, {'type':LobbyChange.PLAYER})
				if request.data['is_ready'] is False and lobby_player.lobby.is_in_queue:
					change_matchmaking_api(lobby_player, "stop")
					add_message(message, "matchmaking_stopped")
				add_message(message, "info_updated")
				return Response(message, status=status.HTTP_200_OK)
			return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.error(f"Error updating player info: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def patch(self, request):
		"""CHANGE SOME of your player info"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_by_user(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			serializer = LobbyPlayerSerializer(lobby_player, data=request.data, context={"request": request}, partial=True)
			if serializer.is_valid():
				lobby_player = serializer.save()
				send_notifications("lobby", lobby_player.lobby.id, {'type': LobbyChange.PLAYER})
				if 'is_ready' in request.data and request.data['is_ready'] is False and lobby_player.lobby.is_in_queue:
					change_matchmaking_api(lobby_player, "stop")
					add_message(message, "matchmaking_stopped")
				add_message(message, "info_updated")
				return Response(message, status=status.HTTP_200_OK)
			return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.error(f"Error updating player info partially: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlayerMeRequestsView(APIView):
	"""URL players/me/requests/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""Get your Lobby Requests"""
	
		message = {}
		try:
			lobby_player = LobbyPlayer.get_or_create(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			data = LobbyPlayerSerializer(lobby_player, context={"request": request}).data
			logger.info(f"data: {data}")
			requests = data.get('requests', [])
			logger.info(f"requests: {requests}")
			if requests:
				message["requests"] = requests
				logger.info(f"message: {message}")
				return Response(message, status=status.HTTP_200_OK)
			add_message(message, "no_requests")
			logger.info(message)
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			logger.error(f"Error fetching lobby requests: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlayerMeRequestView(APIView):
	"""URL players/me/requests/<int:request_id>/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, request_id):
		"""Get a Lobby Request"""
	
		message = {}
		try:
			lobby_player = LobbyPlayer.get_or_create(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			lobby_request = LobbyRequest.get(request_id)
			if not lobby_request or not lobby_request.recipient or lobby_request.recipient.id != lobby_player.id:
				add_message(message, "unknown_request")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			message["request"] = LobbyRequestSerializer(lobby_request, context={"request": request}).data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching lobby requests: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request, request_id):
		"""Reject a Lobby Request"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_or_create(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			lobby_request = LobbyRequest.get(request_id)
			if not lobby_request or lobby_request.recipient.id != lobby_player.id:
				add_message(message, "unknown_request", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			lobby_request.delete()
			send_notifications("lobby_player", lobby_player.id, {'type': LobbyChange.LOBBY_REQUEST})
			add_message(message, "request_denied", request_type=lobby_request.type, sender=lobby_request.sender.user.username)
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error rejecting lobby request: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def put(self, request, request_id):
		"""Accept a Lobby Request"""

		message = {}
		try:
			lobby_player = LobbyPlayer.get_or_create(request.user)
			if not lobby_player or not lobby_player.lobby:
				add_message(message, "not_in_lobby", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			lobby_request = LobbyRequest.get(request_id)
			if not lobby_request or lobby_request.recipient.id != lobby_player.id:
				add_message(message, "unknown_request", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if lobby_request.type == "invite":
				change_lobby_api(lobby_player, lobby_request.sender.lobby)
			elif lobby_request.type == "join":
				change_lobby_api(lobby_request.sender, lobby_player.lobby)
			lobby_request.delete()
			lobby_player.refresh()
			send_notifications("lobby_player", lobby_player.id, {'type':LobbyChange.LOBBY_REQUEST})
			add_message(message, "request_accepted", request_type=lobby_request.type, sender=lobby_request.sender.user.username)
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error accepting lobby request: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)