from django.db import models

class PongPlayerStats(models.Model):
    player = models.CharField(max_length=50)
    gamesWon = models.FloatField()
    gamesTotal = models.FloatField()
    gamesWonMulti = models.FloatField()
    gamesWonRegular = models.FloatField()

    def __str__(self):
        return self.player
    
class PongPlayer(models.Model):
    name = models.CharField(max_length=50)
    level = models.FloatField()
    friends = models.IntegerField()
    online = models.BooleanField()
    stats = PongPlayerStats(name)

    def __str__(self):
        return self.name
