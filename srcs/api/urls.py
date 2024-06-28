from django.urls import path
from .views import (
    PlayerListCreate,
    GameSessionListCreate,
    GameSessionRetrieveUpdateDestroy,
    FriendListCreate,
    FriendRetrieveUpdateDestroy,
    UserListCreate
)
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )


urlpatterns = [
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("players/", PlayerListCreate.as_view(), name="player-list-create"),
    # path("Player/<int:pk>/", views.PlayerRetrieveUpdateDestroy.as_view(), name="update"),
    path("users/", UserListCreate.as_view(), name="user-list-create"),
    # path("User/<int:pk>/", views.UserRetrieveUpdateDestroy.as_view(), name="update"),
    path("friends/", FriendListCreate.as_view(), name="friend-list-create"),
    path("friends/<int:pk>/", FriendRetrieveUpdateDestroy.as_view(), name="friend-update"),
    path("game-sessions/", GameSessionListCreate.as_view(), name="game-session-list-create"),
    path("game-sessions/<int:pk>/", GameSessionRetrieveUpdateDestroy.as_view(), name="friend-update")
]