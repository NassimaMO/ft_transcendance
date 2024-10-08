from .auth.urls import urlpatterns as auth_urls
from .match.urls import urlpatterns as match_urls

urlpatterns = auth_urls + match_urls