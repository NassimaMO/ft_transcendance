from django.urls import path
from .views import (
    PlayerListCreate,
    GameSessionListCreate,
    GameSessionRetrieveUpdateDestroy,
    FriendListCreate,
    FriendRetrieveUpdateDestroy
)

urlpatterns = [
    path("players/", PlayerListCreate.as_view(), name="player-list-create"),
    # path("Player/<int:pk>/", views.PlayerRetrieveUpdateDestroy.as_view(), name="update"),
    # path("User/", views.UserCreate.as_view(), name="user-views-create"),
    # path("User/<int:pk>/", views.UserRetrieveUpdateDestroy.as_view(), name="update"),
    path("friends/", FriendListCreate.as_view(), name="friend-list-create"),
    path("friends/<int:pk>/", FriendRetrieveUpdateDestroy.as_view(), name="friend-update"),
    path("game-sessions/", GameSessionListCreate.as_view(), name="game-session-list-create"),
    path("game-sessions/<int:pk>/", GameSessionRetrieveUpdateDestroy.as_view(), name="friend-update")
]