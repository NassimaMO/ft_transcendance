from rest_framework import serializers
from .models import PongPlayerStats

class PongPlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongPlayerStats
        fields = ["id", "player", "gamesWon", "gamesTotal", "gamesWonMulti", "gamesMultiTotal", "gamesWonRegular", "gamesRegularTotal"]