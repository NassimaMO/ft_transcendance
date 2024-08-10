from django.urls import path
from . import views

urlpatterns = [
    path('', views.matchmaking_view, name='matchmaking'),
]