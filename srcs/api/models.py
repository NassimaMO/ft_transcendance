from django.contrib.auth.models import User
from django.db import models

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=125, null=True, blank=True)
    level = models.FloatField(default=0)
    # friends = models.ManyToManyField("self", blank=True)
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

# Example:
# from django.contrib.auth import authenticate
# user = User.objects.create_user(username='NassiGigachad', email='NassiGigachad@gmail.com', password='enavantouioui123')
# user = authenticate(username='NassiGigachad', password='enavantouioui123')
# if user is not None:
#     print("Authenticated successfully!")
# else:
#     print("Authentication failed.")
# player = Player.objects.create(user=user, bio='It\'s me')
#
