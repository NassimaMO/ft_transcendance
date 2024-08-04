from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .pong_game.views import RegularGameSessionViewSet, UserViewSet, start_game
# from .player_stats.views import PlayerStatsViewSet

router = DefaultRouter()
router.register(r'regulargames', RegularGameSessionViewSet, basename='regulargamesession')
router.register(r'player', UserViewSet)
# router.register(r'playerstats', PlayerStatsViewSet)

urlpatterns = [
	path('', include(router.urls)),
]	