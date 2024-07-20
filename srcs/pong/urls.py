from django.urls import include, path
from . import views
from django.apps import apps

urlpatterns = [
    path('', views.play, name='play'),
    path('solo/', views.game, name='game'),
    path('multi/', views.game, name='game'),
    path('private/', views.private, name='private'),
]
