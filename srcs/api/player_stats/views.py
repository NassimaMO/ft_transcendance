from django.shortcuts import render
from rest_framework import generics
from .models import PlayerStats
from .serializers import PlayerStatsSerializer

class PlayerStatsListCreate(generics.ListCreateAPIView):
    queryset = PlayerStats.objects.all()
    serializer_class = PlayerStatsSerializer

# class PlayerStatsRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = PlayerStats.objects.all()
#     serializer_class = PlayerStatsSerializer
#     lookup_field = "pk"
