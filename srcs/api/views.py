from django.shortcuts import render
from rest_framework import generics
from .models import Player, User, Friend, GameSession
from .serializers import PlayerSerializer, UserSerializer, FriendSerializer, GameSessionSerializer

class PlayerListCreate(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

# class PlayerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Player.objects.all()
#     serializer_class = PlayerSerializer
#     lookup_field = "pk"

# class UserCreate(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = "pk"

class FriendListCreate(generics.ListCreateAPIView):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer

class FriendRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer

class GameSessionListCreate(generics.ListCreateAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer

class GameSessionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
