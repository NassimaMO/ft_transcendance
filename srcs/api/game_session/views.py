from django.shortcuts import render
from rest_framework import generics
from .models import GameSession
from .serializers import GameSessionSerializer

class GameSessionListCreate(generics.ListCreateAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer