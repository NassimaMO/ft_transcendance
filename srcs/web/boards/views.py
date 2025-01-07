from django.shortcuts import render
from api.user_profile.views import UserStatisticsView, UserProfileView

def boards_view(request):
    if not request.user.is_authenticated:
        return render(request, "account/login.html")
    response = UserStatisticsView.get(request)
    context = response.data
    return render(request, "boards.html", context)