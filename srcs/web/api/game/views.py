from rest_framework import status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.authentication import SessionAuthentication # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from pong.serializers import PongGameSessionSerializer, PongGameStateSerializer, PongPlayerSessionSerializer
from pong.models import PongGameSession, PongPlayerSession, PongPlayerStatus
from api.utils import *


class GameSessionView(APIView):
	"""games/sessions/<int:match_id>/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, match_id):
		"""Get a PongGameSession data"""

		message = {}
		try:
			session = PongGameSession.get_by_match_id(match_id)
			if not session:
				add_message(message, "no_game_session", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if not session.match.is_in_match(request.user):
				add_message(message, "forbidden_game_session", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			session_data = PongGameSessionSerializer(instance=session, context={'context':'session'}).data
			message["session"] = session_data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching game session of match {match_id}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	def put(self, request, match_id):
		message = {}
		try:
			session = PongGameSession.get_by_match_id(match_id)
			if not session:
				add_message(message, "no_game_session", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if not session.match.is_in_match(request.user):
				add_message(message, "forbidden_game_session", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			player_session = PongPlayerSession.get_by_user(request.user)
			if not player_session:
				add_message(message, "forbidden_game_session", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			player_session.status = PongPlayerStatus.WAITING
			player_session.save()
			send_ws_message("pong_session", match_id, "start")
			add_message(message, "pong_session_started")
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error updating game session of match {match_id}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		

class GameStateView(APIView):
	"""games/sessions/<int:match_id>/state/"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, match_id):
		"""Get a PongGameSession state"""

		message = {}
		try:
			session = PongGameSession.get_by_match_id(match_id)
			if not session:
				add_message(message, "no_game_session", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if not session.match.is_in_match(request.user):
				add_message(message, "forbidden_game_session", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			session_data = PongGameStateSerializer(instance=session, context={'context':'state'}).data
			message["state"] = session_data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching game state of match {match_id}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	
class GameStatePlayerView(APIView):

	def patch(self, request, match_id, player_id):
			"""Change a PongGameSession state"""

			message = {}
		# try:
			session = PongGameSession.get_by_match_id(match_id)
			if not session:
				add_message(message, "no_game_session", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if not session.match.is_in_match(request.user):
				add_message(message, "forbidden_game_session", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			if not request.data:
				add_message(message, "", level="ERROR")
				return Response(message, status=status.HTTP_400_BAD_REQUEST)
			player = Player.get(player_id)
			if not player :
				add_message(message, "no_player", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			if (player.user and request.user.id != player.user.id):
				add_message(message, "forbidden_change", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			host = session.match.get_host()
			if (not player.user and host and host.user.id != request.user.id):
				add_message(message, "forbidden_change", level="ERROR")
				return Response(message, status=status.HTTP_403_FORBIDDEN)
			if 'move' in request.data.keys():
				player_session = PongPlayerSession.get(player_id)
				if player_session:
					logger.info(f"[API] player_session: {player_session.__dict__}")
				else:
					logger.info(f"{player_session}")
				logger.info(f"[API] data: {request.data}")
				serializer = PongPlayerSessionSerializer(player_session, data={'move':request.data['move']}, context={'request':request}, partial=True)
				logger.info(f"[API] serializer: {serializer.__dict__}")
				if serializer.is_valid():
					session = serializer.save()
					logger.info(f"[API] : {session.__dict__}")
					add_message(message, "player_move_state_updated")
					return Response(message, status=status.HTTP_200_OK)
				return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
			for key in request.data:
				add_message(message, f"invalid_{key}", level="ERROR")
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		# except Exception as e:
		# 	logger.error(f"Error patching game state of match {match_id}: {e}")
		# 	add_message(message, "server_error", level="ERROR")
		# 	return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
