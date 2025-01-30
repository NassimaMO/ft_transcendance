from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=125, null=True, blank=True)
    level = models.FloatField(default=0)
    rank = models.IntegerField(default=0)
    gamesWon = models.FloatField(default=0)
    gamesTotal = models.FloatField(default=0)
    gamesWonMulti = models.FloatField(default=0)
    gamesWonRegular = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

class Friend(models.Model):
    user_from = models.ForeignKey(User, related_name='friend_from', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='friend_to', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return f'{self.user_from.username} is friends with {self.user_to.username}'

User.add_to_class('friends', models.ManyToManyField(
    'self',
    through=Friend,
    symmetrical=False,
    related_name='friendship'
))

class GameSession(models.Model):
    player_one = models.ForeignKey(Player, related_name='player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(Player, related_name='player_two', on_delete=models.CASCADE)
    mode = models.TextField(max_length=125)
    score = models.IntegerField(default=0)
    started = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player_one', 'player_two')

    def __str__(self):
        return f'{self.playerOne.user.username} is playing with {self.playerTwo.user.username}'

Player.add_to_class('GameHistory', models.ManyToManyField(
    'self',
    through=GameSession,
    symmetrical=False,
    related_name='gameSessions'
))

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