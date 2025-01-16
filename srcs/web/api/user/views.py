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

logger = logging.getLogger("default")

class UserRequestsView(APIView):
	"""PATH users/<int/str:user_id_or_username>/requests"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def post(self, request, **kwargs):
		"""SEND a friend request"""

		user_checking = check_user(**kwargs)
		user = user_checking.get("user")
		if not user:
			logger.info(f"Response: {user_checking.get('error_response')}")
			return user_checking.get("error_response")
		if user == request.user:
			message = {
				"errors": {
					"self_friend_attempt": f"You cannot add yourself as a friend. This is sad btw. Seek help."
				}
			}
			return Response(message, status=status.HTTP_400_BAD_REQUEST)
		if user in request.user.friends.all():
			message = {
				"errors": {
					"already_friend": f"No need to send a friend request, you two are already friends. I know, it's unbelievable."
				}
			}
			return Response(message, status=status.HTTP_200_OK)
		if user in request.user.requests.all():
			message = {
				"errors": {
					"already_sent": f"You already asked this user to be your friend. Stop insist. You need to face the truth."
				}
			}
			return Response(message, status=status.HTTP_200_OK)
		user.requests.add(request.user)
		user.save()
		player = LobbyPlayer.get_by_user(user)
		if player:
			send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
		message = {
			"status": "pending",
			"message": f"A friend request has been sent to user {user_checking.get('user_message')}"
		}
		return Response(message, status=status.HTTP_201_CREATED)


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

		serializer = RegisterSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
		return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request):
		"""GET your info"""

		try:
			user_data = UserSerializer(request.user, context={'request': request}).data
			return Response(user_data, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching user info: {str(e)}")
			message = {"errors": {
				type(e).__name__: "Unable to fetch user info."
			}}
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def put(self, request):
		"""CHANGE ALL your info"""

		serializer = UserSerializer(request.user, data=request.data, context={"request": request})
		if serializer.is_valid():
			serializer.save()
			player = LobbyPlayer.get_by_user(request.user)
			if player.lobby:
				send_notifications("lobby", player.lobby.id, {'type': UserChange.INFO})
			elif player:
				send_notifications("lobby_player", player.id, {'type': UserChange.INFO})
			notify_friends_api(request.user)
			return Response({"message": "User info updated successfully."}, status=status.HTTP_200_OK)
		return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

	def patch(self, request):
		"""CHANGE SOME of your info"""

		serializer = UserSerializer(request.user, data=request.data, context={"request": request}, partial=True)
		if serializer.is_valid():
			serializer.save()
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.INFO, 'username': player.user.username})
			notify_friends_api(request.user)
			return Response({"message": "User info partially updated."}, status=status.HTTP_200_OK)
		return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request):
		"""DELETE account"""

		try:
			request.user.delete()
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.INFO})
			notify_friends_api(request.user)
			return Response({"message": "Account deleted successfully."}, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error deleting user: {str(e)}")
			message = {"errors": {
				type(e).__name__: f"{e}. Unable to delete account."
			}}
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMeFriendsView(APIView):
	"""PATH users/me/friends"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""GET your friends"""

		friends = request.user.friends.all()
		if friends.exists():
			friends_data = UserSerializer(friends, many=True, context={"request": request}).data
			return Response(friends_data, status=status.HTTP_200_OK)
		return Response({"message": "You have no friend... :'("}, status=status.HTTP_200_OK)


class UserMeRequestsView(APIView):
	"""PATH users/me/requests/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request):
		"""GET your friend requests"""

		requests = request.user.requests.all()
		if requests.exists():
			requests_data = UserSerializer(requests, many=True, context={"request": request}).data
			return Response(requests_data, status=status.HTTP_200_OK)
		return Response({"message": "No friend request. Be nicer, it will come."}, status=status.HTTP_200_OK)

	def delete(self, request):
		"""REMOVE ALL friend requests"""

		if not request.user.requests.all():
			return Response({"message": "No friend request. Be nicer, it will come."}, status=status.HTTP_200_OK)
		request.user.requests.clear()
		player = LobbyPlayer.get_by_user(request.user)
		if player:
			send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
		return Response({"message": "All friend requests removed."}, status=status.HTTP_200_OK)


class UserMeRequestView(APIView):
	"""PATH users/me/requests/<int/str:user_id_or_username>"""
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def put(self, request, **kwargs):
		"""ACCEPT a friend request"""

		user_checking = check_user(**kwargs)
		user = user_checking.get("user")
		if not user:
			return user_checking.get("error_response")
		if user not in request.user.requests.all():
			message = {
				"errors": {
					"not_a_request": f"Request from user {user_checking.get('user_message')} not found. Is it your imaginary friend ?"
				}
			}
			return Response(message, status=status.HTTP_404_NOT_FOUND)
		request.user.requests.remove(user)
		request.user.friends.add(user)
		player = LobbyPlayer.get_by_user(request.user)
		if player:
			send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST}, {'type': UserChange.FRIEND})
		friend_player = LobbyPlayer.get_by_user(user)
		if friend_player:
			send_notifications("lobby_player", friend_player.id, {'type': UserChange.FRIEND})
		return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)

	def delete(self, request, **kwargs):
		"""DENY a friend request"""

		user_checking = check_user(**kwargs)
		user = user_checking.get("user")
		if not user:
			return user_checking.get("error_response")
		if user not in request.user.requests.all():
			message = {
				"errors": {
					"not_a_request": f"Request from user {user_checking.get('user_message')} not found. It's kinda sad."
				}
			}
			return Response(message, status=status.HTTP_404_NOT_FOUND)
		request.user.requests.remove(user)
		player = LobbyPlayer.get_by_user(request.user)
		if player:
			send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
		return Response({"message": "Friend request denied."}, status=status.HTTP_200_OK)


class UserMeFriendView(APIView):
	"""PATH users/me/friends/<int/str:user_id_or_username>/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, **kwargs):
		"""GET your friend's info"""

		user_checking = check_user(**kwargs)
		user = user_checking.get("user")
		if not user:
			return user_checking.get("error_response")
		if not user.is_friend_with(request.user):
			message = {
				"errors": {
					"not_a_friend": f"Friend {user_checking.get('user_message')} not found. Is it your imaginary friend ?"
				}
			}
			return Response(message, status=status.HTTP_404_NOT_FOUND)
		data = UserSerializer(user, context={'request': request}).data
		return Response(data, status=status.HTTP_200_OK)

	def post(self, request, **kwargs):
		"""ADD friend (Send/Accept Friend Request)"""

		user_checking = check_user(**kwargs)
		user = user_checking.get("user")
		if not user:
			return user_checking.get("error_response")
		if user == request.user:
			message = {
				"errors": {
					"self_friend_attempt": f"You cannot add yourself as a friend. This is sad btw. Seek help."
				}
			}
			return Response(message, status=status.HTTP_400_BAD_REQUEST)
		if user in request.user.friends.all():
			message = {
				"errors": {
					"already_friend": f"No need to send a friend request, you two are already friends. I know, it's unbelievable."
				}
			}
			return Response(message, status=status.HTTP_200_OK)
		if user not in request.user.requests.all():
			request.user.requests.add(user)
			request.user.save()
			player = LobbyPlayer.get_by_user(request.user)
			if player:
				send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND_REQUEST})
			message = {
				"status": "pending",
				"message": f"A friend request has been sent to user {user_checking.get('user_message')}"
			}
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
			message = {
				"status": "accepted",
				"message": f"Friend request from user {user_checking.get('user_message')} accepted. You are now friends."
			}
			return Response({"status": "friend_request_accepted"}, status=status.HTTP_200_OK)

	def delete(self, request, **kwargs):
		"""REMOVE friend"""

		user_checking = check_user(**kwargs)
		user = user_checking.get("user")
		if not user:
			return user_checking.get("error_response")
		if user not in request.user.friends.all():
			message = {
				"errors": {
					"not_a_friend": f"Friend {user_checking.get('user_message')} not found. Is it your imaginary friend ?"
				}
			}
			return Response(message, status=status.HTTP_404_NOT_FOUND)
		request.user.friends.remove(user)
		request.user.save()
		player = LobbyPlayer.get_by_user(request.user)
		if player:
			send_notifications("lobby_player", player.id, {'type': UserChange.FRIEND})
		message = {
			"status": "removed",
			"message": f"User {user_checking.get('user_message')} is no longer your friend. Good riddance."
		}
		return Response(message, status=status.HTTP_200_OK)


class UserStatsView(APIView):
	"""PATH users/<int/str:user_id_or_username>/stats/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request, **kwargs):
		"""GET a user's stats"""

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
		return Response(data, status=status.HTTP_200_OK)


class UserMeStatsView(APIView):
	"""PATH users/me/stats/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication]

	def get(self, request):
		"""GET your stats"""

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
		return Response(data, status=status.HTTP_200_OK)