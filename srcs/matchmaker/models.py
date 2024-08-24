from django.db import models
from django.utils import timezone
from account.models import User

# Create your models here.

class GameMode(models.TextChoices) :
    SOLO = "solo", "Un joueur (VS IA)"
    MULTI = "multi", "Multijoueur"

class Connecitvity(models.TextChoices) :
    LOCAL = "local", "Local"
    ONLINE = "online", "En ligne"

class MatchmakingMode(models.TextChoices) :
    RANK = "classé", "Classé"
    UNRANK = "non classé", "Non Classé"
    TOURNAMENT = "tournoi", "Tournoi"

class MatchChoice(models.Model) :
    connect = models.CharField(max_length=20, choices=Connecitvity.choices, default=Connecitvity.LOCAL)
    mode = models.CharField(max_length=20, choices=GameMode.choices, default=GameMode.SOLO)
    mm = models.CharField(max_length=20, choices=MatchmakingMode.choices, default=MatchmakingMode.UNRANK)

    def __str__(self):
        return f"{self.mode} - {self.connect} - {self.mm}"

class Match(models.Model) :
    date = models.DateTimeField(default=timezone.now)
    info = models.ForeignKey(MatchChoice, related_name="match_info", on_delete=models.CASCADE)

    def __str__(self):
        return f"Match on {self.date} with {self.info}"

class Player(models.Model) :
    user = models.ForeignKey(User, related_name="player_user", on_delete=models.CASCADE)
    pseudo = models.CharField(max_length=20)

class History(models.Model) :
    match = models.ForeignKey(Match, related_name="history_match", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="history_player", on_delete=models.CASCADE)
    score = models.IntegerField()
