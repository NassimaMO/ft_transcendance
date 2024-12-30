from .auth.urls import urlpatterns as auth_urls
from .user.urls import urlpatterns as user_urls
from .lobby.urls import urlpatterns as lobby_urls
from .user_profile.urls import urlpatterns as user_profile_urls

urlpatterns = auth_urls + user_urls + lobby_urls + user_profile_urls