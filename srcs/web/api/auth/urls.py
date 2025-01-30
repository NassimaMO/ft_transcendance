from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserSessionsView, UserSessionView

urlpatterns = [
    path('tokens/', TokenObtainPairView.as_view(), name='api-tokens'),
    path('tokens/refresh/', TokenRefreshView.as_view(), name='api-tokens-refresh'),
    path('users/me/sessions/', UserSessionsView.as_view(), name='api-user-sessions'),
    path('users/me/sessions/<int:session_id>/', UserSessionView.as_view(), name='api-user-session'),
]