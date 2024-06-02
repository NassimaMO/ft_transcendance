from django.urls import path
from . import views

urlpatterns = [
    path(
        "PongPlayerStats/",
        views.PongPlayerStatsCreate.as_view(),
        name="pongplayerstats-views-create"
        ),
    path(
        "PongPlayerStats/<int:pk>/",
        views.PongPlayerStatsRetrieveUpdateDestroy.as_view(),
        name="update"
    )
]