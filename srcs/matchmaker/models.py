from django.db import models
from django.utils import timezone
from account.models import User

# Create your models here.

class GameMode(models.TextChoices) :
    SOLO = "solo", "Un joueur (VS IA)"
    LOCAL = "multi local", "Multijoueur Local"
    ONLINE = "multi online", "Multijoueur en ligne"

class MatchMaking(models.TextChoices) :
    RANK = "ranked", "Ranked"
    UNRANK = "unranked", "Unranked"
    PRIVATE = "private", "Private"
    TOURNAMENT = "tournament", "Tournament"

class Match(models.Model) :
    date = models.DateTimeField(default=timezone.now)
    mode = models.CharField(max_length=20, choices=GameMode.choices, default=GameMode.SOLO)
    mm = models.CharField(max_length=20, choices=MatchMaking.choices, default=MatchMaking.UNRANK)

class Player(models.Model) :
    user = models.ForeignKey(User, related_name="player_user", on_delete=models.CASCADE)
    pseudo = models.CharField(max_length=20)

class History(models.Model) :
    match = models.ForeignKey(Match, related_name="history_match", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="history_player", on_delete=models.CASCADE)
    score = models.IntegerField()
