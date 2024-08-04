from rest_framework import serializers
from .models import RegularGameSession
from account.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'friends', 'status', 'rank']

class RegularGameSessionSerializer(serializers.ModelSerializer):
    player_one = UserSerializer()
    player_two = UserSerializer()
    class Meta:
        model = RegularGameSession
        fields = ['id', 'position_player_one', 'position_player_two', 'score_player_one', 'score_player_two', 'ball_position_x', 'ball_position_y', 'ball_velocity_x', 'ball_velocity_y', 'started']