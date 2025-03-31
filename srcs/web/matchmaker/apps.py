from django.apps import AppConfig
from transcendance.utils import add_methods_rom


class MatchmakerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matchmaker'
    has_methods_added = False

    def ready(self):
        if not MatchmakerConfig.has_methods_added:
            add_methods_rom('matchmaker.models')
            MatchmakerConfig.has_methods_added = True
