from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.boards_view, name='dashboard'),
]