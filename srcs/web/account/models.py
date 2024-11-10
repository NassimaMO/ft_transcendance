from django.db import models
from django.contrib.auth.models import AbstractUser


class Status(models.TextChoices):
    ON = "Actif", "Actif"
    OFF = "Inactif", "Inactif"
    IG = "En jeu", "En Jeu"
    INV = "Invisible", "Invisible"
    BUSY = "Occupé", "Occupé"


class User(AbstractUser):
    avatar = models.ImageField(upload_to='', default="static/account/media/default_avatar.png")
    banner = models.ImageField(upload_to='', default="static/account/media/default_banner.jpg")
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.ON)
    friends = models.ManyToManyField('self', blank=True)
    requests = models.ManyToManyField('self',  symmetrical=False, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='account_user_set',
        blank=True,
        related_query_name='user',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='account_user_set',
        blank=True,
        related_query_name='user',
    )

    @property
    def offline_friends_count(self):
        return self.friends.filter(status=Status.OFF).count()

    @property
    def online_friends_count(self):
        return self.friends.count() - self.offline_friends_count

    def __str__(self):
        return self.username
    
    def __repr__(self):
        return f"<User {self.__str__()}>"
    
    @classmethod
    def get(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None
        
    def get_status(self) :
        return self.status
    
    def get_pseudo(self) :
        return self.username