from rest_framework import serializers # type: ignore
from account.serializers import UserSerializer
from .models import *


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Player
        fields = ['user', 'pseudo', 'is_ai']


class UserRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRank
        fields = ['division', 'marks']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["name"] = instance.rank.name
        return data


class UserRanksSerializer(serializers.Serializer):
    ranks = UserRankSerializer(many=True)

    def to_representation(self, queryset):
        ranks_dict = {game.name: {'rank': 'unranked'} for game in Game.objects.all()}
        for rank in queryset.all():
            ranks_dict[rank.game.name] = UserRankSerializer(rank).data
        return ranks_dict
    

class MatchChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchChoice
        fields = ['connectivity', 'mode', 'matchmaking']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['game'] = instance.game.name.capitalize()
        return data

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
            self.errors.clear()
            self._validated_data = self.validate(attrs)
            return True
        if raise_exception:
            raise serializers.ValidationError(self.errors)
        return False

    def validate(self, attrs):
        warnings = {}
        if attrs.get("mode") == GameMode.SOLO:
            if attrs.get("connectivity") != Connectivity.LOCAL:
                warnings["connectivity"] = "La connectivité a été forcée en locale pour ce choix de modes."
                attrs["connectivity"] = Connectivity.LOCAL
            if attrs.get("matchmaking") != MatchmakingMode.UNRANK:
                warnings["matchmaking"] = "Le matchmaking a été forcé en non classé pour ce choix de modes."
                attrs["matchmaking"] = MatchmakingMode.UNRANK
        attrs["_warnings"] = warnings
        return attrs

    def save(self, **kwargs):
        fields = {field.name for field in self.Meta.model._meta.fields}
        for field in fields:
            if field not in kwargs and field in self.validated_data:
                kwargs[field] = self.validated_data[field]
        match_choice = MatchChoice.objects.filter(**kwargs).first()
        if match_choice:
            return match_choice
        return super().save(**kwargs)
    
    def create(self, validated_data):
        validated_data.pop('_warnings', None)
        return super().create(validated_data)
    

class EntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entry
        fields = ['score']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.player.user).data if instance.player.user else None
        data['pseudo'] = instance.player.pseudo
        return data


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['score']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['players'] = EntrySerializer(instance.entries, many=True).data
        return data
    

class MatchSerializer(serializers.ModelSerializer):
    info = MatchChoiceSerializer()

    class Meta:
        model = Match
        fields = ['date', 'info']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['teams'] = TeamSerializer(instance.teams, many=True).data
        return data


class LobbyRequestSerializer(serializers.Serializer):
    recipient = serializers.CharField()
    sender = serializers.CharField()
    type = serializers.CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['sender'] = LobbyPlayerSerializer(instance.sender).data
        data['type'] = instance.type
        return data
    
    def create(self, validated_data):
        logger.info(validated_data)
        lobby_request = LobbyRequest()
        lobby_request.recipient = validated_data["recipient"]
        lobby_request.sender = validated_data["sender"]
        lobby_request.type = validated_data["type"]
        lobby_request.save()
        return lobby_request
    
    def validate_type(self, value):
        if value not in ['invite', 'join']:
            raise serializers.ValidationError("Invalid value for request type. Expected values : 'invite', 'join'.")


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
    auto_fill = serializers.BooleanField()

    def get_players(self, obj):
        request = self.context.get('request')
        if request :
            sorted_players = sorted(obj.members, key=lambda player: player.user.id == self.context.get('request').user.id, reverse=True)
            return LobbyPlayerSerializer([player for player in sorted_players], many=True, context=self.context).data
        return LobbyPlayerSerializer(obj.members, many=True, context=self.context).data
    
    def to_representation(self, instance) :
        data = super().to_representation(instance)
        data['members'] = self.get_players(instance)
        if instance.status == LobbyStatus.IN_QUEUE:
            waiting_lobby = WaitingLobby.get_by_lobby(instance)
            if waiting_lobby:
                data['queue_start'] = waiting_lobby.start.timestamp()
        if self.context.get('type') == 'template':
            data['all_ready'] = instance.all_ready
        data['status'] = instance.status
        return data
    
    def create(self, validated_data):
        return Lobby(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance