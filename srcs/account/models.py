from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.conf.urls.static import static


class GameRank(models.TextChoices):
    IRON = _("iron"), _("Iron")
    BRONZE = _("bronze"), _("Bronze")
    SILVER = _("silver"), _("Silver")
    GOLD = _("gold"), _("Gold")
    PLAT = _("platinium"), _("Platinium")
    DIAM = _("diamond"), _("Diamond")
    MASTER = _("master"), _("Master")
    GRANDMASTER = _('grandmaster'), _('GrandMaster')
    CHALL = _("challenger"), _("Challenger")


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
    rank = models.CharField(max_length=11, choices=GameRank.choices, default=GameRank.IRON)

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