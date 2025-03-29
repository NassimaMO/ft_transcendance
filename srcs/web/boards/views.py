from django.shortcuts import render
from api.user.views import UserMeStatsView, UserMeRankView, UserMeHistoryView
from .serializers import UserStatsSerializer, UserHistorySerializer
from matchmaker.serializers import MatchSerializer
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger('default')

@login_required
def boards_view(request):
    stats = UserStatsSerializer(request.user)
    rank = UserMeRankView.get(request, 'pong')
    matches = request.user.get_matches()
    match_dates = [match.date.strftime('%d/%m/%Y') for match in matches]
    match_scores = [match.teams.all().first().score if match.teams.exists() else 0 for match in matches]
    history_data = UserHistorySerializer(matches, many=True)
    context = {
        "stats": stats.data,
        "rank": rank.data,
        "history": history_data.data,
        "match_dates": match_dates,
        "match_scores": match_scores
    }
    logger.info(f"{context}")
    return render(request, "boards/boards.html", context)