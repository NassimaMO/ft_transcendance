from django.db import models

class PongPlayerStats(models.Model):
    player = models.CharField(max_length=50)
    gamesWon = models.FloatField()
    gamesTotal = models.FloatField()
    gamesWonMulti = models.FloatField()
    gamesWonRegular = models.FloatField()

    def __str__(self):
        return self.player
    
class Player(models.Model):
    name = models.CharField(max_length=50)
    level = models.FloatField()
    friends = models.IntegerField()
    online = models.BooleanField()
    stats = PongPlayerStats()

    def __str__(self):
        return self.name
