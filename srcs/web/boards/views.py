from django.shortcuts import render
from api.user.views import UserMeStatsView, UserMeRankView, UserMeHistoryView
from django.contrib.auth.decorators import login_required

@login_required
def boards_view(request):
    response_stats = UserMeStatsView.get(request)
    response_rank = UserMeRankView.get(request, 'pong')
    #response_history = UserMeHistoryView.get(request)
    context = {
        "stats": response_stats.data,
        "rank": response_rank.data,
        #"history": response_history,
    }
    return render(request, "boards/boards.html", context)