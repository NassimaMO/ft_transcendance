from django.shortcuts import render
from api.user.views import UserMeStatsView, UserMeRankView, UserMeHistoryView
from .serializers import UserStatsSerializer, UserHistorySerializer
from matchmaker.serializers import MatchSerializer, UserRankSerializer
from matchmaker.models import UserRank, Game
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger('default')

@login_required
def boards_view(request):
    stats = UserStatsSerializer(request.user)
    game = Game.objects.get(name='pong')
    rank, _ = UserRank.objects.get_or_create(user=request.user, game=game)
    user_rank = UserRankSerializer(rank)
    marks_percent = rank.get_marks_percent()
    matches = request.user.get_matches()
    match_dates = [match.date.strftime('%d/%m/%Y') for match in matches]
    match_scores = [entry.score for entry in request.user.history.all()]
    history_data = UserHistorySerializer(matches, many=True, context={'user':request.user})
    context = {
        "stats": stats.data,
        "rank": user_rank.data,
        "marks_percent": marks_percent,
        "history": history_data.data,
        "match_dates": match_dates,
        "match_scores": match_scores
    }
    logger.info(f"{context}")
    return render(request, "boards/boards.html", context)