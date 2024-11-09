from .auth.urls import urlpatterns as auth_urls
from .match.urls import urlpatterns as match_urls
from .user_profile.urls import urlpatterns as user_profile_urls

urlpatterns = auth_urls + match_urls + user_profile_urls