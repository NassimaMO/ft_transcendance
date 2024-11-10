import rom
from django.db import models
from django.utils import timezone
from account.models import User
from datetime import datetime
import logging

logger = logging.getLogger('default')


# ********************************************* POSTGRES ORM MODELS *********************************************


class GameMode(models.TextChoices) :
    SOLO = "Solo", "Un joueur (VS IA)"
    MULTI_1V1 = "1v1", "Multijoueur (1v1)"
    MULTI_2V2 = "2v2", "Multijoueur (2v2)"


class Connecitvity(models.TextChoices) :
    LOCAL = "Local", "Local"
    ONLINE = "En ligne", "En ligne"


class MatchmakingMode(models.TextChoices) :
    UNRANK = "Non Classé", "Non Classé"
    RANK = "Classé", "Classé"
    TOURNAMENT = "Tournoi", "Tournoi"


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
    

class WaitingUser(rom.Model):
    user = rom.ForeignModel(User)
    start = rom.DateTime(default=datetime.now())
    matchmaking = rom.ManyToOne("Matchmaking", on_delete="cascade")

    @classmethod
    def get_or_create(cls, user, matchmaking):
        waiting_users = cls.query.all()
        for waiting_user in waiting_users :
            if waiting_user == user :
                waiting_user.matchmaking = matchmaking
                return waiting_user
        waiting_user = cls(user=user, matchmaking=matchmaking)
        waiting_user.save()
        return waiting_user
    
    def __str__(self) :
        return f"<WaitingUser {self.channel.user}(time:{self.start})>"


class Matchmaking(rom.Model) :
    mm = rom.String(index=True, keygen=rom.IDENTITY)
    queue = rom.OneToMany("WaitingUser")

    @classmethod
    def get_or_create(cls, mm):
        matchmaking = cls.get_by(mm=mm)
        if not matchmaking:
            matchmaking = cls(mm=mm)
            matchmaking.save()
        return matchmaking
    
    def __str__(self) :
        return f"<Matchmaking {self.mm}:{self.queue}>"


class LobbyRequest(rom.Model):
    recipient = rom.ManyToOne("LobbyPlayer", on_delete="cascade")
    sender = rom.String()
    type = rom.String()


class Player(rom.Model) :
    user = rom.ForeignModel(User)
    pseudo = rom.String()
    
    @classmethod
    def get_or_create(cls, user, pseudo=None):
        players = cls.query.all()
        for player in players:
            if player.user == user:
                return player
        if not pseudo:
            pseudo = user.get_pseudo()
        player = cls(user=user.id, pseudo=pseudo)
        player.save()
        return player

class LobbyPlayer(rom.Model) :
    player = rom.OneToOne("Player", on_delete='cascade')
    is_ready = rom.Boolean(default=True)
    is_leader = rom.Boolean(default=True)
    lobby = rom.OneToOne("Lobby", on_delete="set null")
    requests = rom.OneToMany("LobbyRequest")

    @classmethod
    def get_or_create(cls, user=None, player=None):
        lobby_players = cls.query.all()
        for lobby_player in lobby_players:
            if user and lobby_player.player.user == user or player and lobby_player.player == player :
                return lobby_player
        if not player :
            player = Player.get_or_create(user)
        lobby_player = cls(player=player)
        lobby_player.save()
        return lobby_player
    
    def get_request(self, sender, type) :
        for request in self.requests:
            try:
                decoded_type = request.type.decode('utf-8')
                decoded_sender = request.sender.decode('utf-8')
            except UnicodeDecodeError:
                decoded_type = request.type
                decoded_sender = request.sender
            if decoded_sender == sender and decoded_type == type :
                return request
        return None

    def join_lobby(self, lobby) :
        self.is_leader = False
        self.is_ready = False
        self.lobby = lobby
        self.save()

    def leave_lobby(self) :
        if len(self.lobby.players) == 1 :
            self.lobby.delete()
        elif self.is_leader :
            for player in self.lobby.players :
                if player != self :
                    player.is_leader = True
                    player.save()
                    break
        self.delete()

class Lobby(rom.Model) :
    id = rom.PrimaryKey(index=True)
    players = rom.OneToMany("LobbyPlayer")

    @classmethod
    def get_or_create(cls, user):
        lobby_player = LobbyPlayer.get_or_create(user=user)
        if lobby_player.lobby:
            return lobby_player.lobby
        new_lobby = cls()
        new_lobby.save()
        lobby_player.lobby = new_lobby
        lobby_player.save()
        return new_lobby
    
    def add_player(self, user) :
        player = LobbyPlayer.get_or_create(user=user)
        player.join_lobby(self)