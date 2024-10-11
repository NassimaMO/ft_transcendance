from django.urls import re_path
from . import consumers

ws_urlpatterns = [
    re_path(r'ws/matchmaking/(?P<match_choice_id>\d+)$', consumers.MatchmakingConsumer.as_asgi()),
]
