from django.shortcuts import render
from rest_framework import generics
from .models import PongPlayerStats
from .serializers import PongPlayerStatsSerializer

class PongPlayerStatsCreate(generics.ListCreateAPIView):
    queryset = PongPlayerStats.objects.all()
    serializer_class = PongPlayerStatsSerializer