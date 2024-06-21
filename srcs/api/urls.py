from django.urls import path
from . import views

urlpatterns = [
    path(
        "Player/",
        views.PlayerCreate.as_view(),
        name="player-views-create"
        ),
    path(
        "Player/<int:pk>/",
        views.PlayerRetrieveUpdateDestroy.as_view(),
        name="update"
        ),
    path(
        "User/",
        views.UserCreate.as_view(),
        name="user-views-create"
        ),
    path(
        "User/<int:pk>/",
        views.UserRetrieveUpdateDestroy.as_view(),
        name="update"
        ),
    path(
        "Friend/",
        views.FriendCreate.as_view(),
        name="friend-views-create"
        ),
    path(
        "Friend/<int:pk>/",
        views.FriendRetrieveUpdateDestroy.as_view(),
        name="update"
        )
]