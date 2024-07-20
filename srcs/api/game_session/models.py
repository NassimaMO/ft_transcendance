from django.db import models
from ..player.models import Player

class GameSession(models.Model):
    player_one = models.ForeignKey(Player, related_name='player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(Player, related_name='player_two', on_delete=models.CASCADE)
    mode = models.TextField(max_length=125)
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    started = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player_one', 'player_two')

    def __str__(self):
        return f'{self.playerOne.user.username} is playing with {self.playerTwo.user.username}'
    
class GamePaddle(models.Model):
    game = models.OneToOneField(GameSession, on_delete=models.CASCADE)
    position_x = models.FloatField()
    position_y = models.FloatField()
    direction_x = models.FloatField()
    direction_y = models.FloatField()