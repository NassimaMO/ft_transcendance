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
        #{'history': [{'date': '2025-03-27T15:35:22.503738Z', 'info': {'connectivity': 'Local', 'mode': 'Solo', 'matchmaking': 'Non Classé', 'game': 'Pong'}, 'teams': [{'score': 0, 'players': [{'score': 0, 'user': {'username': 'ee', 'avatar': '/media/static/account/media/default_avatar.png', 'banner': '/media/static/account/media/default_banner.jpg', 'status': 'Hors Ligne'}, 'pseudo': 'ee'}]}, {'score': 0, 'players': [{'score': 0, 'user': None, 'pseudo': 'IA'}]}]}]}
    }
    logger.info(f"{context}")
    return render(request, "boards/boards.html", context)