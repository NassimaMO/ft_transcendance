from rest_framework import serializers
from .models import Player
from .models import User
from .models import Friend
from .models import GameSession

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'user', 'bio', 'level', 'rank', 'gamesWon', 'gamesTotal', 'gamesWonMulti', 'gamesWonRegular']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class FriendSerializer(serializers.ModelSerializer):
    user_from = UserSerializer()
    user_to = UserSerializer()
    class Meta:
        model = Friend
        fields = ['id', 'user_from', 'user_to', 'created']

class GameSessionSerializer(serializers.ModelSerializer):
    player_one = PlayerSerializer()
    player_two = PlayerSerializer()
    class Meta:
        model = GameSession
        fields = ['id', 'player_one', 'player_two', 'mode', 'score', 'started']