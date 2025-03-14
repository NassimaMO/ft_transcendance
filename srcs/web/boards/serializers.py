from rest_framework import serializers
from account.models import User

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
        data["win_loss_ratio"] = instance.get_total_games_won() / (len(instance.history.all()) - obj.get_total_games_won()) if data["total_games_played"] != data["games_won"] else data["games_won"]
        return data