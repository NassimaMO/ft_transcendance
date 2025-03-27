import logging
from rest_framework import serializers # type: ignore
from account.serializers import UserSerializer
from matchmaker.serializers import MatchChoiceSerializer
from .models import *

logger = logging.getLogger('default')


class BallSerializer(serializers.Serializer):
    coordinate_x = serializers.FloatField()
    coordinate_y = serializers.FloatField()
    velocity_x = serializers.FloatField()
    velocity_y = serializers.FloatField()
    last_update = serializers.DateTimeField()


class PongPlayerSessionSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    coordinate_x = serializers.FloatField()
    coordinate_y = serializers.FloatField()
    move = serializers.CharField(allow_null=True, required=False)
    last_update = serializers.DateTimeField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        context = self.context.get('context')
        data['id'] = instance.player.id
        data['move'] = PaddleMove.to_string(instance.move)
        if context != 'state' :
            if instance.player.user:
                data['user'] = UserSerializer(instance.player.user).data
            else:
                data['user'] = None
            data['pseudo'] = instance.player.pseudo
            data['is_ai'] = instance.player.is_ai
        return data
    
    def create(self, validated_data):
        return PongPlayerSession(**validated_data)

    def update(self, instance, validated_data):
        instance.update(**validated_data)
        instance.save()
        return instance

    def validate_move(self, value):
        if value not in [None, "", "up", "down"]:
            raise serializers.ValidationError("Invalid value for move state. Expected values: ('', 'up', 'down').")
        return PaddleMove.to_int(value)


class PongTeamSessionSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    paddle_length = serializers.FloatField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['players'] = PongPlayerSessionSerializer(list(instance.player_sessions), many=True, context=self.context).data
        if instance.field_position == FieldPosition.LEFT:
            data['field_position'] = "LEFT"
        if instance.field_position == FieldPosition.RIGHT:
            data['field_position'] = "RIGHT"
        return data


class PongGameStateSerializer(serializers.Serializer):
    ball = BallSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['teams'] = PongTeamSessionSerializer(list(instance.team_sessions), many=True, context=self.context).data
        return data
    

class PongParametersSerializer(serializers.Serializer):
    ball_radius = serializers.FloatField()
    ball_speed = serializers.FloatField()
    paddle_length = serializers.FloatField()
    paddle_width = serializers.FloatField()
    paddle_gap = serializers.FloatField()
    field_ratio = serializers.FloatField()


class PongGameSessionSerializer(serializers.Serializer):
    parameters = PongParametersSerializer()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['match'] = {'info': MatchChoiceSerializer(instance.match.info).data, 'id': instance.match.id}
        data['state'] = PongGameStateSerializer(instance, context=self.context).data
        return data