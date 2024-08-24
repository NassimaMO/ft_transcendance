from django.urls import include, path
from . import views
from django.apps import apps

urlpatterns = [
    path('', views.play, name='play'),
    path('game/', views.game, name='game'),
]
