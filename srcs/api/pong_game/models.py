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

class RegularGameSession(models.Model):
    player_one = models.ForeignKey(User, related_name='player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(User, related_name='player_two', on_delete=models.CASCADE)
    position_player_one = models.FloatField(default=-180)
    position_player_two = models.FloatField(default=180)
    score_player_one = models.IntegerField(default=0)
    score_player_two = models.IntegerField(default=0)
    ball_position_x = models.FloatField(default=0)
    ball_position_y = models.FloatField(default=0)
    ball_velocity_x = models.FloatField(default=1)
    ball_velocity_y = models.FloatField(default=1)
    started = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player_one', 'player_two')

    def __str__(self):
        return f'{self.player_one.username} is playing with {self.player_two.username}'
