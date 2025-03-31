from rest_framework import serializers
from account.models import User
from matchmaker.models import Match

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
        data["win_loss_ratio"] = 0 if data["total_games_played"] == 0 else (data["games_won"] / data["total_games_played"]) * 100
        return data
    
class UserHistorySerializer(serializers.ModelSerializer):
    mode = serializers.CharField(source="info.mode")
    score = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    date = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Match
        fields = ["id", "result", "date", "info", "score"]

    def get_score(self, instance):
        return [team.score for team in instance.teams.all()] 
    
    def get_result(self, instance):
        user = self.context.get('user')
        team = instance.get_team(user)

        if team and team.score == max([t.score for t in instance.teams.all()]):
                return "Victory"
        return "Defeat"