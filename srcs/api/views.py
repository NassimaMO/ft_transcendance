from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
from .models import Player, User, Friend, GameSession
from .serializers import PlayerSerializer, UserSerializer, FriendSerializer, GameSessionSerializer


@api_view(['POST'])
def register_player(request):
    if request.method == 'POST':
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def start_game(request):
    if request.method == 'POST':
        serializer = GameSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Game started successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_friends(request):
    if request.method == 'POST':
        serializer = FriendSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Friendship registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

class PlayerListCreate(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    # permission_classes = [IsAuthenticated]

# class PlayerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Player.objects.all()
#     serializer_class = PlayerSerializer
#     lookup_field = "pk"

class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = "pk"

class FriendListCreate(generics.ListCreateAPIView):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    # permission_classes = [IsAuthenticated]

class FriendRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    # permission_classes = [IsAuthenticated]

class GameSessionListCreate(generics.ListCreateAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    # permission_classes = [IsAuthenticated]

class GameSessionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    # permission_classes = [IsAuthenticated]
