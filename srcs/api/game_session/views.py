from rest_framework import viewsets
from rest_framework import permissions
from .models import GameSession
from .serializers import GameSessionSerializer

class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission = [permissions.IsAuthenticated]
