from django.shortcuts import render
from rest_framework import generics
from .models import Player
from .serializers import PlayerSerializer

class PlayerListCreate(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer