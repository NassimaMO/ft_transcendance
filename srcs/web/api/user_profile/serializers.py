from rest_framework import serializers
from account.models import User
from pong.models import UserRank
from matchmaker.models import History

class AvatarSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None
    
    class Meta:
        model = User
        fields = ['avatar_url']

    
class UserRankSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRank
        fields = ['rank', 'division', 'mark']

class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'status']


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['team', 'pseudo', 'score']


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = AvatarSerializer(source="*")
    rank = UserRankSerializer(read_only=True)
    friends = FriendsSerializer(many=True, read_only=True)
    requests = FriendsSerializer(many=True, read_only=True)
    history = HistorySerializer(many=True, read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['avatar', 'rank', 'friends', 'requests', 'history', 'status']