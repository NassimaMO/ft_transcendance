from .auth.urls import router as auth_router

urlpatterns = list()

urlpatterns += auth_router.urls