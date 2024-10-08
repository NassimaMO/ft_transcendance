import rom
from django.db import models
from django.utils import timezone
from account.models import User
from datetime import datetime


# ********************************************* POSTGRES ORM MODELS *********************************************


class GameMode(models.TextChoices) :
    SOLO = "solo", "Un joueur (VS IA)"
    MULTI_1V1 = "1v1", "Multijoueur (1v1)"
    MULTI_2V2 = "2v2", "Multijoueur (2v2)"


class Connecitvity(models.TextChoices) :
    LOCAL = "local", "Local"
    ONLINE = "online", "En ligne"


class MatchmakingMode(models.TextChoices) :
    RANK = "ranked", "Classé"
    UNRANK = "unranked", "Non Classé"
    TOURNAMENT = "tournament", "Tournoi"


class MatchChoice(models.Model):
    connect = models.CharField(max_length=20, choices=Connecitvity.choices, default=Connecitvity.LOCAL)
    mode = models.CharField(max_length=20, choices=GameMode.choices, default=GameMode.SOLO)
    mm = models.CharField(max_length=20, choices=MatchmakingMode.choices, default=MatchmakingMode.UNRANK)

    class Meta:
        unique_together = ('connect', 'mode', 'mm')

    @classmethod
    def create(cls, connect=Connecitvity.LOCAL, mode=GameMode.SOLO, mm=MatchmakingMode.UNRANK):
        match_choice, created = cls.objects.get_or_create(
            connect=connect,
            mode=mode,
            mm=mm
        )
        return match_choice

    def __str__(self):
        return f"{self.mode} - {self.connect} - {self.mm}"
    
    def need_matchmaking(self) :
        if (self.mode == GameMode.SOLO or self.connect == Connecitvity.LOCAL) :
            return False
        return True


class Match(models.Model):
    date = models.DateTimeField(default=timezone.now)
    info = models.ForeignKey('MatchChoice', related_name="match_info", on_delete=models.CASCADE)
    teams = models.ManyToManyField('Team', related_name="match_team")

    def __str__(self):
        return f"Match {self.id} on {self.date}"

    def __repr__(self):
        return self.__str__()

class Team(models.Model):
    players = models.ManyToManyField(User, through="History")
    match = models.ForeignKey(Match, related_name="team_match", on_delete=models.CASCADE)

    def __str__(self):
        return f"Team {self.id}"

    def __repr__(self):
        return self.__str__()

class History(models.Model):
    user = models.ForeignKey(User, related_name="history_user", on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name="history_team", on_delete=models.CASCADE)
    pseudo = models.CharField(max_length=20)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Player {self.pseudo} in team {self.team.id}: score {self.score}"

    def __repr__(self):
        return self.__str__()
    

# ********************************************* REDIS ORM MODELS *********************************************


class Channel(rom.Model) :
    user = rom.ForeignModel(User)
    name = rom.String(index=True, keygen=rom.IDENTITY)

    @classmethod
    def get_or_create(cls, user, channel_name):
        channel = cls.query.filter(name=channel_name).first()
        if not channel:
            channel = cls(user=user.id, name=channel_name)
            channel.save()
        return channel
    
    def __str__(self) :
        return f"Channel {self.name} for user {self.user}"

class WaitingUser(rom.Model):
    channel = rom.OneToOne("Channel", on_delete="cascade")
    start = rom.DateTime(default=datetime.now())
    matchmaking = rom.ManyToOne("Matchmaking", on_delete="cascade")

    @classmethod
    def get_or_create(cls, channel, matchmaking):
        users = cls.query.all()
        for user in users :
            if user.channel.name == channel.name :
                user.matchmaking = matchmaking
                return user
        user = cls(channel=channel, matchmaking=matchmaking)
        user.save()
        return user
    
    def __str__(self) :
        return f"User {self.channel.user}(time:{self.start})"

class Matchmaking(rom.Model) :
    mm = rom.String(index=True, keygen=rom.IDENTITY)
    queue = rom.OneToMany("WaitingUser")

    @classmethod
    def get_or_create(cls, mm):
        matchmaking = cls.query.filter(mm=mm).first()
        if not matchmaking:
            matchmaking = cls(mm=mm)
            matchmaking.save()
        return matchmaking
    
    def __str__(self) :
        return f"Matchmaking {self.mm}, with queue : {self.queue}"
