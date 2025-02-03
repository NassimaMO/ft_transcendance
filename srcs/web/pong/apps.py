from django.apps import AppConfig
from django.db.utils import OperationalError


class PongConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pong'

    def ready(self):
        import pong.signals
