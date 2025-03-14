from django.shortcuts import render
from api.user.views import UserMeStatsView, UserMeRankView, UserMeHistoryView
from .serializers import UserStatsSerializer
from matchmaker.serializers import MatchSerializer
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger('default')

@login_required
def boards_view(request):
    stats = UserStatsSerializer(request.user)
    #rank = UserMeRankView.get(request, 'pong')
    matches = request.user.get_matches()
    history_data = MatchSerializer(matches, many=True).data
    context = {
        "stats": stats.data,
        #"rank": rank.data['rank'],
        "history": history_data
    }
    logger.info(f"{context}")
    return render(request, "boards/boards.html", context)