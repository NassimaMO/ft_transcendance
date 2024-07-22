from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .pong_game.views import GameSessionViewSet
from .player.views import PlayerViewSet
from .player_stats.views import PlayerStatsViewSet

router = DefaultRouter()
router.register(r'gamesession', GameSessionViewSet)
router.register(r'player', PlayerViewSet)
router.register(r'playerstats', PlayerStatsViewSet)

urlpatterns = [
	path('', include(router.urls)),
]	