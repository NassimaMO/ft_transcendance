from django.shortcuts import render

# Create your views here.

def play(request) :
    return (render(request, "pong/play.html"))