from rest_framework import serializers
import base64
from account.models import User
# from .models import PlayerStats

"""
class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = ['id', 'gamesWon', 'gamesTotal', 'gamesWonMulti', 'gamesWonRegular']
"""