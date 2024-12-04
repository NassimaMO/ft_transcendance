from rest_framework import serializers
from account.serializers import UserSerializer
import logging
from .models import MatchChoice

logger = logging.getLogger('default')


class MatchChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchChoice
        fields = ['connect', 'mode', 'mm']

    def is_valid(self):
        valid = super().is_valid()
        if valid:
            return True
        if self.errors.get("non_field_errors") :
            for error in self.errors["non_field_errors"] :
                if error.code != "unique" :
                    return False
            return True
        return False

    def save(self, **kwargs):
        match_choice = MatchChoice.objects.filter(**kwargs).first()
        if match_choice:
            return match_choice
        return super().save(**kwargs)


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
    user = UserSerializer()
    pseudo = serializers.CharField()
    is_ready = serializers.BooleanField()
    is_leader = serializers.BooleanField()
    requests = LobbyRequestSerializer(many=True)

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


class LobbySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    members = LobbyPlayerSerializer(many=True)
    match_choice = MatchChoiceSerializer()
    is_open = serializers.BooleanField()
    is_in_queue = serializers.BooleanField()

    def get_players(self, obj):
        request = self.context.get('request')
        if request :
            sorted_players = sorted(obj.members, key=lambda player: player.user.id == self.context.get('request').user.id, reverse=True)
            return LobbyPlayerSerializer([player for player in sorted_players], many=True, context=self.context).data
        return LobbyPlayerSerializer(obj.members, many=True, context=self.context).data
    
    def to_representation(self, instance) :
        data = super().to_representation(instance)
        data['members'] = self.get_players(instance)
        return data
