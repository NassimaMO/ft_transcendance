import logging
from rest_framework_simplejwt.backends import TokenBackend
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger('default')

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
        return await self.inner(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        return User.objects.get(id=user_id)
