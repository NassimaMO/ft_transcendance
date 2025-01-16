from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserProfileSerializer
from matchmaker.models import Team

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @classmethod
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @classmethod
    def get(self, request):
        user = request.user
        all_games_played = user.get_all_games_played()
        history = self._get_history(all_games_played, user)
        games_played = len(all_games_played)
        games_won = self._get_total_games_won(all_games_played, user)
        win_streak = self._get_win_streak(all_games_played, user)
        average_score = self._get_average_score(all_games_played, user)
        win_loss_ratio = games_won / (games_played - games_won) if games_played != games_won else games_won
        data = {
            "history" : history,
            "total_games_played": games_played,
            "games_won": games_won,
            "games_lost": games_played - games_won,
            "win_streak": win_streak,
            "average_score": average_score,
            "win_loss_ratio": win_loss_ratio,
        }
        return Response(data)
    
    @classmethod
    def _get_history(self, all_games_played, user):
        history = []
        for match in all_games_played:
            matches = {}
            winning_team = Team.objects.filter(match=match).order_by('-score').first()
            if winning_team and winning_team.players.filter(id=user.id).exists():
                matches["result"] = "Victory"
                matches["team1_score"] = winning_team.score
                matches["team2_score"] = Team.objects.filter(match=match).exclude(id=winning_team.id).first()

            else:
                matches["result"] = "Defeat"
                matches["team1_score"] = Team.objects.filter(match=match).exclude(id=winning_team.id).first()
                matches["team2_score"] = winning_team.score
            matches["mode"] = match.info.mode
            matches["date"] = match.date
            history.append(matches)
        return history

    @classmethod
    def _get_total_games_won(self, all_games_played, user):
        games_won_count = 0
        for match in all_games_played:
            winning_team = Team.objects.filter(match=match).order_by('-score').first()
            if winning_team and winning_team.players.filter(id=user.id).exists():
                games_won_count += 1
        return games_won_count
    
    @classmethod
    def _get_average_score(self, all_games_played, user):
        average_score = sum(Team.objects.filter(match=match, players=user).first().score for match in all_games_played)
        average_score = average_score / len(all_games_played) if len(all_games_played) > 0 else 0
        return average_score
    
    @classmethod
    def _get_win_streak(self, all_games_played, user):
        win_streak = 0
        for match in all_games_played:
            winning_team = Team.objects.filter(match=match).order_by('-score').first()
            if winning_team and winning_team.players.filter(id=user.id).exists():
                win_streak += 1
            else:
                break
        return win_streak