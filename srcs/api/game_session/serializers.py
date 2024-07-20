from rest_framework import serializers
from .models import GameSession
from ..player.serializers import PlayerSerializer

class GameSessionSerializer(serializers.ModelSerializer):
    player_one = PlayerSerializer()
    player_two = PlayerSerializer()
    class Meta:
        model = GameSession
        fields = ['id', 'player_one', 'player_two', 'mode', 'score', 'started']