from rest_framework import serializers
from account.serializers import UserSerializer
import logging
from .models import MatchChoice, Lobby, LobbyPlayer, WaitingLobby

logger = logging.getLogger('default')


class MatchChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchChoice
        fields = ['connectivity', 'mode', 'matchmaking']

    def is_valid(self, *, raise_exception=False):
        valid = super().is_valid(raise_exception=raise_exception)
        if valid:
            return True
        non_field_errors = self.errors.get("non_field_errors")
        if non_field_errors:
            for error in non_field_errors:
                if error.code != "unique":
                    if raise_exception:
                        raise serializers.ValidationError(self.errors)
                    return False
            attrs = {field: self.initial_data.get(field) for field in self.fields}
            self._validated_data = self.validate(attrs)
            self.errors.clear()
            return True
        if raise_exception:
            raise serializers.ValidationError(self.errors)
        return False

    def save(self, **kwargs):
        fields = {field.name for field in self.Meta.model._meta.fields}
        for field in fields:
            if field not in kwargs and field in self.validated_data:
                kwargs[field] = self.validated_data[field]
        match_choice = MatchChoice.objects.filter(**kwargs).first()
        if match_choice:
            return match_choice
        return super().save(**kwargs)


class LobbyRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = LobbyPlayerSerializer(instance.sender).data
        data['type'] = instance.type
        return data


class LobbyPlayerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    is_ready = serializers.BooleanField()
    is_leader = serializers.BooleanField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        data['user'] = UserSerializer(instance.user, context=self.context).data
        data['pseudo'] = instance.pseudo
        if request and request.user.id == instance.user.id :
            data['requests'] = LobbyRequestSerializer(instance.requests, context=self.context, many=True).data
        return data
    
    def create(self, validated_data):
        return LobbyPlayer(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def validate(self, data):
        if not data.get("is_ready", True) and data.get("is_leader", False):
            raise serializers.ValidationError(
                "Le leader ne peut pas ne pas être prêt."
            )
        return data


class LobbySerializer(serializers.Serializer):
    id = serializers.IntegerField()
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
        if instance.is_in_queue:
            waiting_lobby = WaitingLobby.get_by_lobby(instance)
            if waiting_lobby:
                data['queue_start'] = waiting_lobby.start.timestamp()
        if self.context.get('type') == 'template':
            data['all_ready'] = instance.all_ready
        return data
    
    def create(self, validated_data):
        return Lobby(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
