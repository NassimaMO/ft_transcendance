from rest_framework import serializers
from .models import User, Session
import logging


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'avatar', 'banner', 'status']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user == instance :
            data['id'] = instance.id
            data['friends'] = UserSerializer(instance.friends.all(), many=True).data
            data['requests'] = UserSerializer(instance.requests.all(), many=True).data
            if self.context.get('type') == 'template' :
                data['online_friends_count'] = instance.online_friends_count
                data['offline_friends_count'] = instance.offline_friends_count
        if instance.avatar:
            data['avatar'] = instance.avatar.url
        return data