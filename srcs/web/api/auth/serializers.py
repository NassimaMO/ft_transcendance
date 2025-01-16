from rest_framework import serializers
from account.models import User
from django.utils.timezone import now
from account.models import Session


class SessionSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True)

    class Meta:
        model = Session
        fields = ['id', 'user', 'ip_address', 'user_agent', 'login_time', 'user_id']
        read_only_fields = ['id', 'user', 'login_time']

    def create(self, validated_data):
        user = validated_data.pop('user_id')
        validated_data['user'] = user
        return super().create(validated_data)

    @classmethod
    def extract_from_request(cls, request, user):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        return cls(data={
            "user_id": user.id,
            "ip_address": ip_address,
            "user_agent": user_agent,
        })