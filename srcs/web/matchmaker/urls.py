from django.urls import path
from . import views

urlpatterns = [
    path('<int:match_choice_id>/', views.matchmaking_view, name='matchmaking'),
]