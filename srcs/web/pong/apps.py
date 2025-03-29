from django.apps import AppConfig
from transcendance.utils import add_methods_rom


class PongConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pong'

    def ready(self):
        import pong.signals
        add_methods_rom('pong.models')