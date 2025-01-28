from django.shortcuts import render
from api.user.views import UserMeStatsView
from django.contrib.auth.decorators import login_required

@login_required
def boards_view(request):
    response = UserMeStatsView.get(request)
    context = response.data
    return render(request, "boards.html", context)