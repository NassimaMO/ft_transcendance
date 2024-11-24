from django.db import models
from django.contrib.auth.models import AbstractUser

class Status(models.TextChoices):
    ON = "actif", "Actif"
    OFF = "inactif", "Inactif"
    IG = "en jeu", "En Jeu"
    INV = "invisible", "Invisible"
    BUSY = "occupé", "Occupé"


class User(AbstractUser):
    avatar = models.ImageField(upload_to='', default="static/account/media/avatar.png")
    friends = models.ManyToManyField('self', blank=True)
    requests = models.ManyToManyField('self', blank=True)
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.OFF)

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

    def __str__(self):
        return self.username
    
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def get(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None
        
    def get_status(self) :
        return self.status
    
    def get_all_games_played(self):
        from matchmaker.models import Match
        all_matches = []
        for match in Match.objects.all():
            for team in match.teams:
                if self in team.players:
                    all_matches.append(match)
        #Match.objects.filter(teams__players=self).distinct()
        return all_matches #.order_by('-date')