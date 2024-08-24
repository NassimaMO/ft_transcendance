from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .pong_game.views import RegularGameSessionViewSet, UserViewSet
# from .player_stats.views import PlayerStatsViewSet

router = DefaultRouter()
router.register(r'games', RegularGameSessionViewSet, basename='rgamesessions')
router.register(r'users', UserViewSet)
# router.register(r'playerstats', PlayerStatsViewSet)

urlpatterns = [
	path('', include(router.urls)),
]	