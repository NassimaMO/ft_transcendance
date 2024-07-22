from rest_framework import serializers
from .models import GameSession
from ..player.serializers import PlayerSerializer

class GameSessionSerializer(serializers.ModelSerializer):
    player_one = PlayerSerializer()
    player_two = PlayerSerializer()
    class Meta:
        model = GameSession
        fields = ['id', 'player_one.position_x', 'player_two.position_y', 'mode', 'score_player1', 'score_player2', 'ball_position_x', 'ball_position_y', 'ball_velocity_x', 'ball_velocity_y', 'started']