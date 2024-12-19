from django.urls import path
from . import views

urlpatterns = [
    path('users/<int:user_id>/requests/', views.UserRequestsView.as_view(), name='api-user-requests'),
    path('users/<str:username>/requests/', views.UserRequestsView.as_view(), name='api-user-requests'),
    path('users/me/', views.UserMeView.as_view(), name='api-user-friend'),
    path('users/me/friends/', views.UserMeFriendsView.as_view(), name='api-user-friends'),
    path('users/me/friends/<int:user_id>/', views.UserMeFriendView.as_view(), name='api-user-friend'),
    path('users/me/friends/<str:username>/', views.UserMeFriendView.as_view(), name='api-user-friend'),
    path('users/me/requests/', views.UserMeRequestsView.as_view(), name='api-user-requests'),
    path('users/me/requests/<int:user_id>/', views.UserMeRequestView.as_view(), name='api-user-request'),
    path('users/me/requests/<str:username>/', views.UserMeRequestView.as_view(), name='api-user-request'),
]
