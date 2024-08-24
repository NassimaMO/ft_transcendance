from django.db import models
from account.models import User

"""
** TABLES SQL **

1) RegularGameSession

objets : 
- Balle (position & velocité)
- Players
- started

2) PlayerSession

objets:
- User
- score
- position
"""

class GameSession(models.Model):
    ball_position_x = models.FloatField(default=0)
    ball_position_y = models.FloatField(default=0)
    ball_velocity_x = models.FloatField(default=1)
    ball_velocity_y = models.FloatField(default=1)
    started = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        players = ", ".join([player.user.username for player in self.players.all()])
        return f'Game started at {self.started} with players: {players}'

class PlayerSession(models.Model):
    user = models.ForeignKey(User, related_name='players', on_delete=models.CASCADE)
    game_session = models.ForeignKey(GameSession, related_name='game', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    position = models.FloatField()

    def __str__(self):
        return f'{self.user.username} in game with score {self.score}'