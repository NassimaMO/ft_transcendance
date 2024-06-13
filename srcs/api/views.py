from django.shortcuts import render
from rest_framework import generics
from .models import Player
from .models import User
from .models import Friend
from .serializers import PlayerSerializer
from .serializers import UserSerializer
from .serializers import FriendSerializer


class PlayerCreate(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class PlayerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_field = "pk"

class UserCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"

class FriendCreate(generics.ListCreateAPIView):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer

class FriendRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    lookup_field = "pk"