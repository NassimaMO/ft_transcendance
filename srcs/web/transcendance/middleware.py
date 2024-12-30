import logging
from rest_framework_simplejwt.backends import TokenBackend
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.conf import settings

logger = logging.getLogger('default')


class WebSocketLoggingMiddleware:
    """
    Middleware ASGI pour traquer tous les événements envoyés et reçus par un WebSocket.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        logger.info(f"[MIDDLEWARE] User: {scope.get('user', 'N/A')}")
        logger.info(f"[MIDDLEWARE] Channel Name: {scope.get('channel_name', 'N/A')}")
        logger.info(f"[MIDDLEWARE] Channel Layer: {type(scope.get('channel_layer'))}")

        async def logging_receive():
            message = await receive()
            logger.debug(f"[MIDDLEWARE] Event received: {message}")
            return message

        async def logging_send(event):
            logger.debug(f"[MIDDLEWARE] Event sent: {event}")
            await send(event)

        return await self.app(scope, logging_receive, logging_send)


class JWTAuthMiddleware:
    """
    Middleware pour authentifier les utilisateurs externes via JWT.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        token = headers.get(b'authorization')
        if token:
            try:
                token = token.decode('utf-8').split(' ')[1]
                valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
                user = await self.get_user(valid_data['user_id'])
                scope['user'] = user
            except Exception as e :
                logger.debug(f"Middleware Exception: {e}")
                return
        # else:
        #     logger.info(f"[MIDDLEWARE] - No token provided. Can't authenticate request.")
        return await self.inner(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        return User.objects.get(id=user_id)


class DisableDebugForCLI:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if request.META.get('HTTP_X_CLI_REQUEST') == 'true' or \
        'curl' in user_agent or 'httpie' in user_agent or 'python-requests' in user_agent:
            original_debug = settings.DEBUG
            settings.DEBUG = False
            logger.info("DEBUG: ", settings.DEBUG)
            response = self.get_response(request)
            settings.DEBUG = original_debug
            return response
        logger.info("DEBUG UNCHANGED")
        return self.get_response(request)
