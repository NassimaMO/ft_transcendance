from django.shortcuts import render
from api.user.views import UserMeStatsView

def boards_view(request):
    if not request.user.is_authenticated:
        return render(request, "account/login.html")
    response = UserMeStatsView.get(request)
    context = response.data
    return render(request, "boards/boards.html", context)