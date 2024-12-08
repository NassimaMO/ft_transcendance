from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from account.models import Session, Status
from django.contrib.auth import logout
from .serializers import SessionSerializer
import logging

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

        try:
            sessions = Session.objects.filter(user=request.user)
            if not sessions.exists():
                return Response({"message": "No sessions found."}, status=status.HTTP_204_NO_CONTENT)
            serializer = SessionSerializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving sessions: {str(e)}")
            message = {"errors": {
                type(e).__name__: "An error occurred while retrieving sessions. Try again later."
            }}
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """CREATE a new Session (authentication)"""

        token_serializer = TokenObtainPairSerializer(data=request.data)
        if token_serializer.is_valid():
            tokens = token_serializer.validated_data
            user = token_serializer.user
            try:
                serializer = SessionSerializer.extract_from_request(request, user)
                if serializer.is_valid():
                    session = serializer.save()
                    user.status = Status.ON
                    user.save()
                    message = {
                        'access': tokens['access'],
                        'refresh': tokens['refresh'],
                        'session_id': session.id,
                    }
                    return Response(message, status=status.HTTP_201_CREATED)
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating session: {str(e)}")
                message = {"errors": {
                    type(e).__name__: "An error occurred while creating session. Try again later"
                }}
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"errors": token_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserSessionView(APIView):
    """URL users/me/sessions/<int:session_id>"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get(self, request, session_id):
        """GET session details"""

        try:
            session = Session.objects.get(id=session_id, user=request.user)
        except Session.DoesNotExist:
            message = {"errors": {"unknown_session": "Session not found"}}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            message = {"errors": {
                type(e).__name__: f"An error occurred while retrieving session details. Try again later."
            }}
            logger.error(f"Error retrieving session details: {str(e)}")
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, session_id):
        """DELETE a session (logout)."""
        
        try:
            session = Session.objects.get(id=session_id, user=request.user)
        except Session.DoesNotExist:
            message = {"errors": {"unknown_session": "Session not found"}}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            message = {"errors": {
                type(e).__name__: f"An error occurred while deleting the session. Try again later."
            }}
            logger.error(f"Error deleting session: {str(e)}")
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logout(request.user)
        request.user.status = Status.OFF
        request.user.save()
        session.delete()
        return Response({"message": "Session deleted successfully."}, status=status.HTTP_200_OK)
