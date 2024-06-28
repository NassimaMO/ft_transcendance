from rest_framework import serializers
from .models import Player
from .models import User
from .models import Friend
from .models import GameSession

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'user', 'bio', 'level', 'rank', 'gamesWon', 'gamesTotal', 'gamesWonMulti', 'gamesWonRegular']

    def validate(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            player = Player.objects.create(user=user, **validated_data)
            return player
        raise serializers.ValidationError(user_serializer.errors)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

        def validate_username(self, value):
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("This username is already taken.")
            if ' ' in value:
                raise serializers.ValidationError("Username should not contain spaces.")
            return value
    
        def validate_password(self, value):
            if not any(char.isdigit() for char in value):
                raise serializers.ValidationError("Password must have at least 1 digit.")
            if len(value) < 10:
                raise serializers.ValidationError("Password must be at least 8 characters long.")
            return value

class FriendSerializer(serializers.ModelSerializer):
    user_from = UserSerializer()
    user_to = UserSerializer()
    class Meta:
        model = Friend
        fields = ['id', 'user_from', 'user_to', 'created']
    
    def validate_user_from(self, value):
        username = value.get('user').get('username')
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This player does not exist.")
        return value
    
    def validate_user_to(self, value):
        username = value.get('user').get('username')
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This player does not exist.")
        return value

class GameSessionSerializer(serializers.ModelSerializer):
    player_one = PlayerSerializer()
    player_two = PlayerSerializer()
    class Meta:
        model = GameSession
        fields = ['id', 'player_one', 'player_two', 'mode', 'score', 'started']

    def validate_player_one(self, value):
        username = value.get('user').get('username')
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This player does not exist.")
        return value
    
    def validate_player_two(self, value):
        username = value.get('user').get('username')
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This player does not exist.")
        return value