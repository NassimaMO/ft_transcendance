from rest_framework import status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.authentication import SessionAuthentication # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from api.utils import check_user, send_notifications, notify_friends_api
from account.serializers import UserSerializer
from account.models import UserChange
from .serializers import RegisterSerializer
from matchmaker.models import LobbyPlayer
import logging
from api.utils import add_message

logger = logging.getLogger("default")

class UserRequestsView(APIView):
	"""PATH users/<int/str:user_id_or_username>/requests"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def post(self, request, **kwargs):
		"""SEND a friend request"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			if user.id == request.user.id:
				add_message(message, "self_friend_attempt", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			if user in request.user.friends.all():
				add_message(message, "already_friend")
				return Response(message, status=status.HTTP_200_OK)
			if user in request.user.requests.all():
				add_message(message, "already_sent")
				return Response(message, status=status.HTTP_200_OK)
			user.requests.add(request.user)
			user.save()
			player = LobbyPlayer.get_by_user(user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
			add_message(message, "friend_request_sent", user_message=user_checking.get('user_message'))
			return Response(message, status=status.HTTP_201_CREATED)
		except Exception as e:
			logger.error(f"Error sending friend request to user {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMeView(APIView):
	"""PATH users/me/"""

	security_checks = {
		"POST": ([AllowAny], [JWTAuthentication, SessionAuthentication]),
	}

	def initialize_request(self, request, *args, **kwargs):
		permission_classes, authentication_classes = self.security_checks.get(
			request.method,
			([IsAuthenticated], [JWTAuthentication, SessionAuthentication])
		)
		self.permission_classes = permission_classes
		self.authentication_classes = authentication_classes
		return super().initialize_request(request, *args, **kwargs)

	def post(self, request):
		"""Create account (registration)"""

		message = {}
		try:
			serializer = RegisterSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				add_message(message, "registration_success")
				return Response(message, status=status.HTTP_201_CREATED)
			return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.error(f"Error creating account: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def get(self, request):
		"""GET your info"""

		message = {}
		try:
			user_data = UserSerializer(request.user, context={'request': request}).data
			message['user'] = user_data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error rejecting lobby request: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def put(self, request):
		"""CHANGE ALL your info"""

		message = {}
		try:
			serializer = UserSerializer(request.user, data=request.data, context={"request": request})
			if serializer.is_valid():
				serializer.save()
				player = LobbyPlayer.get_by_user(request.user)
				if player.lobby:
					send_notifications("lobby", player.lobby.id, {'type': UserChange.INFO})
				elif player:
					send_notifications("lobby_player", player.id, {'type': UserChange.INFO})
				notify_friends_api(request.user)
				add_message(message, "user_updated")
				return Response(message, status=status.HTTP_200_OK)
			return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.error(f"Error updating user info: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def patch(self, request):
		"""CHANGE SOME of your info"""

		message = {}
		try:
			serializer = UserSerializer(request.user, data=request.data, context={"request": request}, partial=True)
			if serializer.is_valid():
				serializer.save()
				player = LobbyPlayer.get_by_user(request.user)
				if player:
					send_notifications("lobby_player", player.id, {'type': UserChange.INFO, 'username': player.user.username})
				notify_friends_api(request.user)
				add_message(message, "user_updated")
				return Response(message, status=status.HTTP_200_OK)
			return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.error(f"Error updating user info partially: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request):
		"""DELETE account"""

		message = {}
		try:
			request.user.delete()
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.INFO})
			notify_friends_api(request.user)
			add_message(message, "delete_account")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error deleting account: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMeFriendsView(APIView):
	"""PATH users/me/friends"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""GET your friends"""

		message = {}
		try:
			friends = request.user.friends.all()
			if friends.exists():
				friends_data = UserSerializer(friends, many=True, context={"request": request}).data
				message['friends'] = friends_data
				return Response(message, status=status.HTTP_200_OK)
			add_message(message, "no_friend")
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			logger.error(f"Error fetching friends: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMeRequestsView(APIView):
	"""PATH users/me/requests/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""GET your friend requests"""

		message = {}
		try:
			requests = request.user.requests.all()
			if requests.exists():
				requests_data = UserSerializer(requests, many=True, context={"request": request}).data
				message['requests'] = requests_data
				return Response(message, status=status.HTTP_200_OK)
			add_message(message, "no_friend_request")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching friend requests: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request):
		"""REMOVE ALL friend requests"""

		message = {}
		try:
			if not request.user.requests.all():
				add_message(message, "no_friend_request")
				return Response(message, status=status.HTTP_200_OK)
			request.user.requests.clear()
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
			add_message(message, "friend_requests_removed")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error removing friend requests: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMeRequestView(APIView):
	"""PATH users/me/requests/<int/str:user_id_or_username>"""
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def put(self, request, **kwargs):
		"""ACCEPT a friend request"""

		message= {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			if user not in request.user.requests.all():
				add_message(message, "unknown_friend_request", level="ERROR", user_message=user_checking.get("user_message"))
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			request.user.requests.remove(user)
			request.user.friends.add(user)
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST}, {'type': UserChange.FRIEND})
			friend_player = LobbyPlayer.get_by_user(user)
			if friend_player:
				send_notifications("lobby_player", friend_player.id, {'type': UserChange.FRIEND})
			add_message(message, "friend_request_accepted")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error accepting friend request of user {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request, **kwargs):
		"""DENY a friend request"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			if user not in request.user.requests.all():
				add_message(message, "unknown_friend_request")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			request.user.requests.remove(user)
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
			add_message("friend_request_denied")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error denying friend request of user {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMeFriendView(APIView):
	"""PATH users/me/friends/<int/str:user_id_or_username>/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, **kwargs):
		"""GET your friend's info"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			if not user.is_friend_with(request.user):
				add_message(message, "unknown_friend", level="ERROR", user_message=user_checking.get('user_message'))
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			data = UserSerializer(user, context={'request': request}).data
			message['friend'] = data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching friend {user_checking.get('user_message')} info: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def post(self, request, **kwargs):
		"""ADD friend (Send/Accept Friend Request)"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			if user.id == request.user.id:
				add_message(message, "self_friend_attempt", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			if user in request.user.friends.all():
				add_message(message, "already_friend")
				return Response(message, status=status.HTTP_200_OK)
			if user not in request.user.requests.all():
				request.user.requests.add(user)
				request.user.save()
				player = LobbyPlayer.get_by_user(request.user)
				if player:
					send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
				add_message(message, "friend_request_sent", user_message=user_checking.get("user_message"))
				return Response(message, status=status.HTTP_201_CREATED)
			else:
				request.user.requests.remove(user)
				request.user.friends.add(user)
				request.user.save()
				player = LobbyPlayer.get_by_user(request.user)
				if player:
					send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND})
				friend_player = LobbyPlayer.get_by_user(user)
				if friend_player:
					send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND})
				add_message(message, "friend_request_accepted", user_message=user_checking.get('user_message'))
				return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error sending friend request to user {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request, **kwargs):
		"""REMOVE friend"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			if user not in request.user.friends.all():
				add_message(message, "unknown_friend", user_message=user_checking.get('user_message'))
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			request.user.friends.remove(user)
			request.user.save()
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND})
			add_message(message, "friend_removed", user_message=user_checking.get('user_message'))
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error removing friend {user_checking.get('user_message')}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStatsView(APIView):
	"""PATH users/<int/str:user_id_or_username>/stats/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request, **kwargs):
		"""GET a user's stats"""

		message = {}
		try:
			user_checking = check_user(**kwargs)
			user = user_checking.get("user")
			if not user:
				return user_checking.get("error_response")
			games_played = len(user.history.all())
			games_won = user.get_total_games_won()
			win_streak = user.get_win_streak()
			average_score = user.get_average_score()
			win_loss_ratio = games_won / (games_played - games_won) if games_played != games_won else games_won
			data = {
				"total_games_played": games_played,
				"games_won": games_won,
				"win_streak": win_streak,
				"average_score": average_score,
				"win_loss_ratio": win_loss_ratio,
			}
			message['stats'] = data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching user {user_checking.get('user_message')} stats: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMeStatsView(APIView):
	"""PATH users/me/stats/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request):
		"""GET your stats"""

		message = {}
		try:
			user = request.user
			games_played = len(user.history.all())
			games_won = user.get_total_games_won()
			win_streak = user.get_win_streak()
			average_score = user.get_average_score()
			win_loss_ratio = games_won / (games_played - games_won) if games_played != games_won else games_won
			data = {
				"total_games_played": games_played,
				"games_won": games_won,
				"win_streak": win_streak,
				"average_score": average_score,
				"win_loss_ratio": win_loss_ratio,
			}
			message['stats'] = data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching stats: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)