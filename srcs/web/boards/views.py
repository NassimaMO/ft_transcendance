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
    history_data = UserHistorySerializer(matches, many=True)
    context = {
        "stats": stats.data,
        "rank": rank.data,
        "history": history_data.data
    }
    logger.info(f"{context}")
    return render(request, "boards/boards.html", context)