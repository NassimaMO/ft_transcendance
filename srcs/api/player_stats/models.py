from django.db import models
from ..player.models import Player

class PlayerStats(models.Model):
    player = models.OneToOneField(Player, related_name='stats', on_delete=models.CASCADE)
    gamesWon = models.FloatField(default=0)
    gamesTotal = models.FloatField(default=0)
    gamesWonMulti = models.FloatField(default=0)
    gamesWonRegular = models.FloatField(default=0)

    def __str__(self):
        return self.user.player.username

# import logging
# from django.contrib.auth import authenticate

# logger = logging.getLogger('django')

# def createPlayer(username, password, email)
#     logger.info("HEYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY LISTEEEEEEEEEEEEEEEEEENNNNNNNNNNNN!")
#     user = User.objects.create_user(username=username, email=password, password=email)
#     player = Player.objects.create(user=user)
#     return player

# def authenticatePlayer(username, password):
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         logger.info("Authenticated successfully!")
#         return True
#     logger.info("Authentication failed.")
#     return False

# def friendRequest(user_from_name, user_to_name):
#     user_from = Player.objects.get(user=user_from_name)
#     user_to = Player.objects.get(user=user_to_name)
#     Friend.objects.get_or_create(user_from=user_from, user_to=user_to)
#     Friend.objects.get_or_create(user_from=user_to, user_to=user_from)