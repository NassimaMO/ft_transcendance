from rest_framework import serializers
from .models import GameSession, PlayerSession, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'status', 'rank', 'password']

class PlayerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerSession
        fields = ['id', 'user', 'game_session', 'score', 'position']

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['id', 'ball_position_x', 'ball_position_y', 'ball_velocity_x', 'ball_velocity_y', 'started']