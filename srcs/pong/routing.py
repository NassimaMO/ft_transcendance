from django.urls import re_path
from . import consumers

ws_urlpatterns = [
    re_path(r'ws/pong/(?P<game_id>\d+)/$', consumers.PongConsumer.as_asgi()),
]