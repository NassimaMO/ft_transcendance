from django.urls import path
from . import views

urlpatterns = [
    path('users/me/', views.UserMeView.as_view(), name='api-user-friend'),

    path('users/me/friends/', views.UserMeFriendsView.as_view(), name='api-user-friends'),
    path('users/me/friends/<int:user_id>/', views.UserMeFriendView.as_view(), name='api-user-friend-id'),
    path('users/me/friends/<str:username>/', views.UserMeFriendView.as_view(), name='api-user-friend-name'),

    path('users/me/requests/', views.UserMeRequestsView.as_view(), name='api-user-requests'),
    path('users/me/requests/<int:user_id>/', views.UserMeRequestView.as_view(), name='api-user-request-id'),
    path('users/me/requests/<str:username>/', views.UserMeRequestView.as_view(), name='api-user-request-name'),

    path('users/me/ranks/', views.UserMeRanksView.as_view(), name='api-user-me-ranks'),
    path('users/me/ranks/<int:game_id>/', views.UserMeRankView.as_view(), name='api-user-me-rank-id'),
    path('users/me/ranks/<str:game_name>/', views.UserMeRankView.as_view(), name='api-user-me-rank-name'),
    path('users/me/history/', views.UserMeHistoryView.as_view(), name='api-user-me-history'),
    path('users/me/stats/', views.UserMeStatsView.as_view(), name='api-user-me-stats'),


    path('users/<int:user_id>/requests/', views.UserRequestsView.as_view(), name='api-user-id-requests'),
    path('users/<str:username>/requests/', views.UserRequestsView.as_view(), name='api-user-name-requests'),

    path('users/<int:user_id>/ranks/', views.UserRanksView.as_view(), name='api-user-id-ranks'),
    path('users/<str:username>/ranks/', views.UserRanksView.as_view(), name='api-user-name-ranks'),
    path('users/<int:user_id>/ranks/<int:game_id>/', views.UserRankView.as_view(), name='api-user-id-rank-id'),
    path('users/<str:username>/ranks/<int:game_id>/', views.UserRankView.as_view(), name='api-user-name-rank-id'),
    path('users/<int:user_id>/ranks/<str:game_name>/', views.UserRankView.as_view(), name='api-user-id-rank-name'),
    path('users/<str:username>/ranks/<str:game_name>/', views.UserRankView.as_view(), name='api-user-name-rank-name'),

    path('users/<int:user_id>/stats/', views.UserStatsView.as_view(), name='api-user-id-stats'),
    path('users/<str:username>/stats/', views.UserStatsView.as_view(), name='api-user-name-stats'),
]
