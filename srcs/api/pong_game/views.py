from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import GameSession
from .serializers import GameSessionSerializer
from .logic import updateGameState

class GameViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def update_state(self, request, pk=None):
        game = self.get_object()
        updateGameState(game.id)
        return Response(GameSessionSerializer(game).data)

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        player = self.get_object()
        action = request.data.get('action')
        game = GameSession.objects.filter(player1=player).first() or GameSession.objects.filter(player2=player).first()

        if action == 'move_up' and player == game.player1:
            game.paddle1_position += 0.1
        elif action == 'move_down' and player == game.player1:
            game.paddle1_position -= 0.1
        elif action == 'move_up' and player == game.player2:
            game.paddle2_position += 0.1
        elif action == 'move_down' and player == game.player2:
            game.paddle2_position -= 0.1

        game.save()
        return Response(status=status.HTTP_200_OK)