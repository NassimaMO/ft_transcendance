from django.urls import path
from . import views

urlpatterns = [
    path('lobby/', views.lobby_home_view, name='lobby-home'),
    path('lobby/<int:lobby_id>', views.lobby_view, name='lobby'),
    path('lobby/<int:lobby_id>/get', views.lobby_get_request, name='lobby-get'),
    path('lobby/modes', views.modes_view, name='lobby-modes'),
    path('lobby/players', views.lobby_players_view, name='lobby-players'),
    path('lobby/list', views.lobby_list_view, name='lobby-list'),
    path('lobby/list/friends', views.friends_list_view, name='lobby-list-friends'),
    path('lobby/requests/friends', views.friend_requests_view, name='friend-requests'),
    path('lobby/requests/lobby', views.lobby_requests_view, name='lobby-requests'),
    path('lobby/invite_banner', views.invite_banner_view, name='lobby-invite-banner'),
]