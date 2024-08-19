from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class GameRank(models.TextChoices):
    BRONZE = _("bronze"), _("Bronze")
    SILVER = _("silver"), _("Silver")
    GOLD = _("gold"), _("Gold")
    PLAT = _("platinium"), _("Platinium")
    DIAM = _("diamond"), _("Diamond")
    MASTER = _("master"), _("Master")
    CHALL = _("challenger"), _("Challenger")

    @classmethod
    def sorted_ranks(cls):
        return [
            cls.BRONZE,
            cls.SILVER,
            cls.GOLD,
            cls.PLAT,
            cls.DIAM,
            cls.MASTER,
            cls.CHALL
        ]
    
    @classmethod
    def next_rank(cls, current_rank):
        ranks = cls.sorted_ranks()
        try:
            current_index = ranks.index(current_rank)
            if current_index < len(ranks) - 1:
                return ranks[current_index + 1]
            else:
                return current_rank
        except ValueError:
            return None
        

    @classmethod
    def previous_rank(cls, current_rank):
        ranks = cls.sorted_ranks()
        try:
            current_index = ranks.index(current_rank)
            if current_index > 0 :
                return ranks[current_index - 1]
            else:
                return current_rank
        except ValueError:
            return None
    
    @classmethod
    def marks_per_rank(cls):
        return {
            cls.BRONZE: 2,
            cls.SILVER: 3,
            cls.GOLD: 4,
            cls.PLAT: 5,
            cls.DIAM: 10,
            cls.MASTER: 20,
            cls.CHALL: 50
        }


class Status(models.TextChoices):
    ON = _("actif"), _("Actif")
    OFF = _("inactif"), _("Inactif")
    IG = _("en jeu"), _("En Jeu")
    INV = _("invisible"), _("Invisible")
    BUSY = _("occupé"), _("Occupé")


class User(AbstractUser):
    avatar = models.ImageField(upload_to='', default="static/account/media/avatar.png")
    friends = models.ManyToManyField('self', blank=True)
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.OFF)
    rank = models.CharField(max_length=11, choices=GameRank.choices, default=GameRank.BRONZE)
    division = models.IntegerField(default=4)
    mark = models.IntegerField(default=0)

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

    class Meta :
        ordering = ["username"]

    def __str__(self):
        return self.username
    
    def promote(self) :
        if (self.mark == GameRank.marks_per_rank()[self.rank]) :
            if (self.division == 1) :
                if (self.rank != GameRank.sorted_ranks()[-1]) :
                    self.division = 4
                    self.mark = 0
                self.rank = GameRank.next_rank(self.rank)
            else :
                self.division -= 1
                self.mark = 0
        else :
            self.mark += 1
        self.save()

    def demote(self) :
        if (self.mark == 0) :
            if (self.division == 4) :
                if (self.rank != GameRank.sorted_ranks()[0]) :
                    self.division = 1
                    self.mark = GameRank.marks_per_rank()[self.rank]
                self.rank = GameRank.previous_rank(self.rank)
            else:
                self.division += 1
                self.mark = GameRank.marks_per_rank()[self.rank]
        else :
            self.mark -= 1
        self.save()