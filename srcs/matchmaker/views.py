from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def matchmaking_view(request):
    return render(request, 'matchmaker/matchmaking.html')