from rest_framework import status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.authentication import SessionAuthentication # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # type: ignore
from account.models import Session, Status
from django.contrib.auth import logout # type: ignore
from .serializers import SessionSerializer
from matchmaker.models import LobbyPlayer
import logging
from api.utils import add_message

logger = logging.getLogger("default")

class UserSessionsView(APIView):
	"""URL users/me/sessions"""

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

	def get(self, request):
		"""GET all your sessions"""

		message = {}
		try:
			sessions = Session.objects.filter(user=request.user)
			if not sessions.exists():
				add_message(message, "no_sessions", level="ERROR")
				return Response(message, status=status.HTTP_204_NO_CONTENT)
			serializer = SessionSerializer(sessions, many=True)
			message['sessions'] = serializer.data
			return Response(message, status=status.HTTP_200_OK)
		except Exception as e:
			logger.error(f"Error fetching sessions: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def post(self, request):
		"""CREATE a new Session (authentication)"""

		message = {}
		try:
			token_serializer = TokenObtainPairSerializer(data=request.data)
			if token_serializer.is_valid():
				tokens = token_serializer.validated_data
				user = token_serializer.user
				serializer = SessionSerializer.extract_from_request(request, user)
				if serializer.is_valid():
					session = serializer.save()
					user.status = Status.ON
					user.save()
					message['session'] = {
						'url': f"users/me/sessions/{session.id}"
					}
					message['tokens'] = {
						'access': tokens['access'],
						'refresh': tokens['refresh'],
					}
					return Response(message, status=status.HTTP_201_CREATED)
				return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
			return Response({"errors": token_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			logger.error(f"Error creating new session : {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSessionView(APIView):
	"""URL users/me/sessions/<int:session_id>"""

	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get(self, request, session_id):
		"""GET session details"""

		message = {}
		try:
			session = Session.objects.get(id=session_id, user=request.user)
			if not session:
				add_message(message, "unknown_session", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			serializer = SessionSerializer(session)
			message['session'] = serializer.data
			return Response(message, status=status.HTTP_200_OK)
		except Session.DoesNotExist:
			add_message(message, "unknown_session", level="ERROR")
			return Response(message, status=status.HTTP_404_NOT_FOUND)
		except Exception as e:
			logger.error(f"Error fetching session {session_id} : {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def delete(self, request, session_id):
		"""DELETE a session (logout)."""
		
		message = {}
		try:
			session = Session.objects.get(id=session_id, user=request.user)
			if not session:
				add_message(message, "unknown_session", level="ERROR")
				return Response(message, status=status.HTTP_404_NOT_FOUND)
			lobby_player = LobbyPlayer.get_by_user(request.user)
			if lobby_player:
				lobby_player.delete()
			request.user.status = Status.OFF
			request.user.save()
			logout(request.user)
			session.delete()
			add_message(message, "delete_session")
			return Response(message, status=status.HTTP_200_OK)
		except Session.DoesNotExist:
			add_message(message, "unknown_session", level="ERROR")
			return Response(message, status=status.HTTP_404_NOT_FOUND)
		except Exception as e:
			logger.error(f"Error deleting session {session_id}: {e}")
			add_message(message, "server_error", level="ERROR")
			return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
