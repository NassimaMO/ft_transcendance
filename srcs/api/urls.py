from django.urls import path
from . import views

urlpatterns = [
    path("PongPlayerStats/", views.PongPlayerStatsCreate.as_view(), name="pongplayerstats-views-create")
]