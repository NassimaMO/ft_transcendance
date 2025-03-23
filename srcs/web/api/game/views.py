from rest_framework import status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.authentication import SessionAuthentication # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from pong.serializers import PongGameSessionSerializer, PongGameStateSerializer, PongPlayerSessionSerializer
from pong.models import PongGameSession, PongPlayerSession
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
		
	def patch(self, request, match_id):
		"""Change a PongGameSession state"""

		message = {}
		try:
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
			if 'move' in request.data.keys():
				player_session = PongPlayerSession.get_by_user(request.user)
				serializer = PongPlayerSessionSerializer(player_session, data={'move':request.data['move']}, context={'request':request}, partial=True)
				if serializer.is_valid():
					serializer.save()
					add_message(message, "player_move_state_updated")
					return Response(message, status=status.HTTP_200_OK)
				return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
			for key in request.data:
				add_message(message, f"invalid_{key}", level="ERROR")
			return Response(message, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			logger.error(f"Error patching game state of match {match_id}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
