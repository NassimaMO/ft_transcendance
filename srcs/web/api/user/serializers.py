from rest_framework import serializers
from account.models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    
# class UserStats(serializers.ModelSerializers):
#     class Meta:
#         model = User
#         fields = 