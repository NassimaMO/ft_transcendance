from django.urls import path # type: ignore
from . import views


urlpatterns = [
    path('games/sessions/<int:match_id>/', views.GameSessionView.as_view(), name='api-game-session'),
    path('games/sessions/<int:match_id>/state/', views.GameStateView.as_view(), name='api-game-session-state'),
]
