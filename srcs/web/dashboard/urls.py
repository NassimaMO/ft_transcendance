from django.urls import path
from . import views

urlpatterns = [
    path('board/', views.dashboard_view, name='dashboard'),
]