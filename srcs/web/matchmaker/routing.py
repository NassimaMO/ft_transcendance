from django.urls import re_path
from . import consumers

ws_urlpatterns = [
    re_path(r'ws/matchmaking/(?P<match_choice_id>\d+)$', consumers.MatchmakingConsumer.as_asgi()),
    re_path(r'ws/lobby', consumers.LobbyConsumer.as_asgi()),
]
