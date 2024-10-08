from django.urls import path
from .views import MatchChoiceView


urlpatterns = [
    path('play/', MatchChoiceView.as_view(), name='api-play'),
]
