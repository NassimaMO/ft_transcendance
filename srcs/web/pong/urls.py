from django.urls import include, path
from . import views
from django.apps import apps

urlpatterns = [
    # path('', views.game_client, name='game-client'),
    path('<int:game_id>/', views.game_client, name='game'),
]
