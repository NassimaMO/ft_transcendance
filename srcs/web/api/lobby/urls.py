from django.urls import path
from . import views


urlpatterns = [
    path('users/me/lobbies/', views.UserLobbiesView.as_view(), name='api-users-lobbies'),
    path('users/me/lobbies/main/', views.UserLobbiesMainView.as_view(), name='api-user-lobbies-main'),
    path('users/me/lobbies/main/requests/', views.UserLobbyRequestsView.as_view(), name='api-user-lobby-requests'),
    path('users/me/lobbies/main/requests/<int:user_id>/', views.UserLobbiesMainRequestView.as_view(), name='api-user-lobby-request'),
    path('users/me/lobbies/main/requests/<str:username>/', views.UserLobbiesMainRequestView.as_view(), name='api-user-lobby-request'),
    path('users/me/lobbies/main/members/', views.UserLobbiesMainMembersView.as_view(), name='api-users-lobby-members'),
    path('users/me/lobbies/main/members/<int:member_id>/', views.UserLobbiesMainMemberView.as_view(), name='api-users-lobby-member'),
    path('users/me/lobbies/main/members/me', views.UserLobbiesMainMembersMeView.as_view(), name='api-users-lobby-members-me'),
    path('users/me/lobbies/<int:lobby_id>/', views.UserLobbyView.as_view(), name='api-user-lobby'),
    path('users/me/lobbies/<int:lobby_id>/requests/', views.UserLobbyRequestsView.as_view(), name='api-user-lobbies-requests'),
    path('users/me/friends/<int:user_id>/lobby/requests/', views.UserFriendLobbyRequests.as_view(), name='api-user-friend-id-lobby-requests'),
    path('users/me/friends/<str:username>/lobby/requests/', views.UserFriendLobbyRequests.as_view(), name='api-user-friend-name-lobby-requests'),
]
