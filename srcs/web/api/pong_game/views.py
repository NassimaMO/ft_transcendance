from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from pong.models import RegularGameSession
#from .logic import updateGameState

""" class RegularGameSessionViewSet(viewsets.ModelViewSet):
    queryset = RegularGameSession.objects.all()
    #serializer_class = RegularGameSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_game(self, request):
        player_one = User.objects.get(id=request.data.get('player_one_id'))
        player_two = User.objects.get(id=request.data.get('player_two_id'))

        new_game = RegularGameSession.objects.create(
            player_one=player_one,
            player_two=player_two
        )

        #serializer = RegularGameSessionSerializer(new_game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def update_state(self, request, pk=None):
        game = self.get_object()
        #updateGameState(game.id)
        game.save()
        #return Response(RegularGameSessionSerializer(game).data)

    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        game = self.get_object()
        player = request.data.get('player')
        player_action = request.data.get('action')

        if player == 'one':
            if player_action == 'move_up':
                game.position_player_one = min(game.position_player_one + 5, 96)
            elif player_action == 'move_down':
                game.position_player_one = max(game.position_player_one - 5, -96)
        elif player == 'two':
            if player_action == 'move_up':
                game.position_player_two = min(game.position_player_two + 5, 96)
            elif player_action == 'move_down':
                game.position_player_two = max(game.position_player_two - 5, -96)

        game.save()
        return Response(status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] """


















from django.shortcuts import get_object_or_404
from django.http import JsonResponse

def start_game(request):
    user = request.user
    game = RegularGameSession.objects.filter(player_two__isnull=True).first()
    
    if game:
        game.player_two = user
        game.save()
        role = 'player_two'
    else:
        game = RegularGameSession.objects.create(player_one=user)
        role = 'player_one'
    
    return JsonResponse({
        'game_session_id': game.id,
        'role': role
    })