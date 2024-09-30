"""
ASGI config for transcendance project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transcendance.settings')
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from matchmaker.routing import ws_urlpatterns as matchmaker_ulrs
from account.routing import ws_urlpatterns as account_ulrs
from pong.routing import ws_urlpatterns as pong_urls

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            matchmaker_ulrs + account_ulrs + pong_urls
        )
    ),
})

