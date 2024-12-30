from django.urls import path
from .views import UserProfileView, UserStatisticsView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('stats/', UserStatisticsView.as_view(), name='game-stats')
]