from rest_framework import serializers
from account.serializers import UserSerializer
import logging

logger = logging.getLogger('default')

class PlayerSerializer(serializers.Serializer):
    pseudo = serializers.CharField()
    user = UserSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        binary_pseudo = instance.pseudo
        try:
            decoded_pseudo = binary_pseudo.decode('utf-8')
        except UnicodeDecodeError:
            decoded_pseudo = binary_pseudo
        data['pseudo'] = decoded_pseudo
        data['user'] = UserSerializer(instance.user, context=self.context).data
        return data


class LobbyRequestSerializer(serializers.Serializer):
    sender = serializers.CharField()
    type = serializers.CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        binary_pseudo = instance.sender
        binary_type = instance.type
        try:
            decoded_pseudo = binary_pseudo.decode('utf-8')
            decoded_type = binary_type.decode('utf-8')
        except UnicodeDecodeError:
            decoded_pseudo = binary_pseudo
            decoded_type = binary_type
        data['sender'] = decoded_pseudo
        data['type'] = decoded_type
        return data


class LobbyPlayerSerializer(serializers.Serializer):
    player = PlayerSerializer()
    is_ready = serializers.BooleanField()
    is_leader = serializers.BooleanField()
    requests = LobbyRequestSerializer(many=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['player'] = PlayerSerializer(instance.player, context=self.context).data
        return data


class LobbySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    players = LobbyPlayerSerializer(many=True)

    def get_players(self, obj):
        request = self.context.get('request')
        if request :
            sorted_players = sorted(obj.players, key=lambda player: player.player.user.id == self.context.get('request').user.id, reverse=True)
            return LobbyPlayerSerializer([player for player in sorted_players], many=True, context=self.context).data
        return LobbyPlayerSerializer(obj.players, many=True, context=self.context).data
    
    def to_representation(self, instance) :
        data = super().to_representation(instance)
        data['players'] = self.get_players(instance)
        return data
