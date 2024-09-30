from django.urls import include, path
from . import views
from django.apps import apps

urlpatterns = [
    path('', views.play, name='play'),
    path('game/<int:game_id>/', views.game, name='game'),
]
