from rest_framework import status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework.authentication import SessionAuthentication # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from pong.serializers import GameSessionSerializer, GameStateSerializer
from pong.models import PongGameSession
from matchmaker.models import Game
from api.utils import *
import logging


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
			session_data = GameSessionSerializer(instance=session, context={'context':'session'}).data
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
			session_data = GameStateSerializer(instance=session, context={'context':'state'}).data
			message["state"] = session_data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching game state of match {match_id}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
