from rest_framework import serializers
from .models import Player
from .models import User
from .models import Friend

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "user", "bio", "level", "gamesWon", "gamesTotal", "gamesWonMulti", "gamesWonRegular"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "is_active", "date_joined"]

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ["id", "user_from", "user_to", "created"]