from django.urls import re_path
from . import consumers

ws_urlpatterns = [
    re_path(r'ws/matchmaking', consumers.MatchmakingConsumer.as_asgi()),
    re_path(r'ws/lobby/(?P<lobby_id>\d+)/$', consumers.LobbyConsumer.as_asgi()),
]
