# matchmaker/routing.py

from django.urls import re_path
from . import consumers

ws_urlpatterns = [
    re_path(r'ws/user/$', consumers.UserConsumer.as_asgi()),
]