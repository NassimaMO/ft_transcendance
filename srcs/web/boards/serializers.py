from rest_framework import serializers
from account.models import User
from matchmaker.models import Match
import logging

logger = logging.getLogger('default')

class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']
 
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["total_games_played"] = len(instance.history.all())
        data["games_won"] = instance.get_total_games_won()
        data["games_lost"] = len(instance.history.all()) - instance.get_total_games_won()
        data["win_streak"] = instance.get_win_streak()
        data["average_score"] = instance.get_average_score()
        data["win_loss_ratio"] = instance.get_win_loss_ratio()
        return data
    
class UserHistorySerializer(serializers.ModelSerializer):
    mode = serializers.CharField(source="info.mode")
    connectivity = serializers.CharField(source="info.connectivity")
    matchmaking = serializers.CharField(source="info.matchmaking")
    score = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    date = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Match
        fields = ["id", "result", "date", "mode", "connectivity", "matchmaking", "score"]

    def get_score(self, instance):
        return [team.score for team in instance.teams.all()] 
    
    def get_result(self, instance):
        user = self.context.get('user')
        team = instance.get_team(user)
        logger.info(f"{team} {user} {team.is_winner()}")
        if team and team.is_winner():
            return "Victory"
        return "Defeat"