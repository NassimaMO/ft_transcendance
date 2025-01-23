from django.urls import path
from . import views


urlpatterns = [
    path('lobbies/', views.LobbiesView.as_view(), name='api-lobbies'),
    path('lobbies/<int:lobby_id>/', views.LobbyView.as_view(), name='api-lobby'),
    path('lobbies/<int:lobby_id>/members/', views.LobbyMembersView.as_view(), name='api-lobby-members'),

    path('lobbies/main/', views.MainLobbyView.as_view(), name='api-main-lobby'),
    path('lobbies/main/members/', views.MainLobbyMembersView.as_view(), name='api-main-lobby-members'),
    path('lobbies/main/members/<int:user_id>/', views.MainLobbyMemberView.as_view(), name='api-main-lobby-members'),
    path('lobbies/main/members/<str:username>/', views.MainLobbyMemberView.as_view(), name='api-main-lobby-members'),
    
    path('players/me/', views.PlayerMeView.as_view(), name='api-player-me'),
    path('players/me/requests/', views.PlayerMeRequestsView.as_view(), name='api-player-me-requests'),
    path('players/me/requests/<int:request_id>/', views.PlayerMeRequestView.as_view(), name='api-player-me-request'),
    
    path('players/<int:user_id>/', views.PlayerView.as_view(), name='api-player-id'),
    path('players/<str:username>/', views.PlayerView.as_view(), name='api-player-name'),
    path('players/<int:user_id>/lobby/', views.PlayerLobbyView.as_view(), name='api-player-id-lobby'),
    path('players/<str:username>/lobby/', views.PlayerLobbyView.as_view(), name='api-player-name-lobby'),
    path('players/<int:user_id>/requests/', views.PlayerRequestsView.as_view(), name='api-player-id-requests'),
    path('players/<str:username>/requests/', views.PlayerRequestsView.as_view(), name='api-player-name-requests'),

]
