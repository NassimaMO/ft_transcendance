from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from .models import GameSession, PlayerSession
from .serializers import GameSessionSerializer, UserSerializer
from .logic import updateGameState

class RegularGameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    # permission = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_game(self, request):
        user = User.objects.get(id=request.data.get('players'))
        available_game = GameSession.objects.annotate(player_count=models.Count('players')).filter(player_count=1).first()
        if available_game:
            new_player = PlayerSession.objects.create(
                user=user,
                position=180,
                game_session=available_game
            )
            serializer = GameSessionSerializer(available_game)
        else:
            game_session=GameSession.objects.create()
            new_player = PlayerSession.objects.create(
                user=user,
                position=-180,
                game_session=game_session
            )
            serializer = GameSessionSerializer(game_session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def update_state(self, request, pk=None):
        game = self.get_object()
        updateGameState(game.id)
        game.save()
        return Response(GameSessionSerializer(game).data)

    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        game = self.get_object()
        paddle = request.data.get('player')
        if paddle == 'right':
            player = game.players.filter(position__gte=0).order_by('position').first()
        else:
            player = game.players.filter(position__lte=0).order_by('-position').first()
        player_action = request.data.get('action')

        if player_action == 'move_up':
            player.position = min(player.position + 5, 96)
        elif player_action == 'move_down':
            player.position = max(player.position - 5, -96)

        game.save()
        return Response(status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission = [permissions.IsAuthenticated]