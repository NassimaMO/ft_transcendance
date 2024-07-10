from django.db import models
from .models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=125, null=True, blank=True)
    level = models.FloatField(default=0)
    rank = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
