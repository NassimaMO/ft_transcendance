import logging
from rest_framework import serializers # type: ignore
from account.serializers import UserSerializer
from matchmaker.serializers import PlayerSerializer, MatchChoiceSerializer
from .models import *

logger = logging.getLogger('default')


class BallSerializer(serializers.Serializer):
    coordinate_x = serializers.FloatField()
    coordinate_y = serializers.FloatField()
    velocity_x = serializers.FloatField()
    velocity_y = serializers.FloatField()


class PlayerSessionSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    coordinate_x = serializers.FloatField()
    coordinate_y = serializers.FloatField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        context = self.context.get('context')
        data['id'] = instance.player.id
        if context != 'state' :
            if instance.player.user:
                data['user'] = UserSerializer(instance.player.user).data
            else:
                data['user'] = None
            data['pseudo'] = instance.player.pseudo
        return data


class TeamSessionSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    paddle_length = serializers.FloatField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['players'] = PlayerSessionSerializer(list(instance.player_sessions), many=True, context=self.context).data
        if instance.field_position == FieldPosition.LEFT:
            data['field_position'] = "LEFT"
        if instance.field_position == FieldPosition.RIGHT:
            data['field_position'] = "RIGHT"
        return data


class GameStateSerializer(serializers.Serializer):
    ball = BallSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['teams'] = TeamSessionSerializer(list(instance.team_sessions), many=True, context=self.context).data
        return data
    

class PongParametersSerializer(serializers.Serializer):
    ball_radius = serializers.FloatField()
    ball_speed = serializers.FloatField()
    paddle_length = serializers.FloatField()
    paddle_width = serializers.FloatField()
    paddle_gap = serializers.FloatField()
    field_ratio = serializers.FloatField()


class GameSessionSerializer(serializers.Serializer):
    parameters = PongParametersSerializer()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['match'] = {'info': MatchChoiceSerializer(instance.match.info).data, 'id': instance.match.id}
        data['state'] = GameStateSerializer(instance, context=self.context).data
        return data