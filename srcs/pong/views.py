from django.shortcuts import render

# Create your views here.

def play(request) :
    return (render(request, "pong/play.html"))

def game(request) :
    return (render(request, "pong/game.html"))

def private(request) :
    return (render(request, "pong/private.html"))