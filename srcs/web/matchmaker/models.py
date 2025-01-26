import rom
import redis
import django_filters
import logging
import time
import threading
from django.db import models
from django.utils import timezone
from account.models import User
from datetime import datetime


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
	connectivity = models.CharField(max_length=20, choices=Connecitvity.choices, default=Connecitvity.LOCAL)
	mode = models.CharField(max_length=20, choices=GameMode.choices, default=GameMode.SOLO)
	matchmaking = models.CharField(max_length=20, choices=MatchmakingMode.choices, default=MatchmakingMode.UNRANK)

	class Meta:
		unique_together = ('connectivity', 'mode', 'matchmaking')

	@classmethod
	def create(cls, connectivity=Connecitvity.LOCAL, mode=GameMode.SOLO, matchmaking=MatchmakingMode.UNRANK):
		match_choice, created = cls.objects.get_or_create(
			connectivity=connectivity,
			mode=mode,
			matchmaking=matchmaking
		)
		return match_choice
	
	@classmethod
	def get(cls, pk):
		try:
			return cls.objects.get(pk=pk)
		except cls.DoesNotExist:
			return None

	def __str__(self):
		return f"{self.mode} - {self.connectivity} - {self.matchmaking}"
	
	def need_matchmaking(self) :
		if (self.mode == GameMode.SOLO or self.connectivity == Connecitvity.LOCAL) :
			return False
		return True


class MatchChoiceFilter(django_filters.FilterSet):
	connectivity = django_filters.CharFilter(lookup_expr='iexact')
	mode = django_filters.CharFilter(lookup_expr='iexact')
	matchmaking = django_filters.CharFilter(lookup_expr='iexact')

	class Meta:
		model = MatchChoice
		fields = ['connectivity', 'mode', 'matchmaking']


def get_default_match_choice():
	defaults = {
		'connectivity': MatchChoice._meta.get_field('connectivity').get_default(),
		'mode': MatchChoice._meta.get_field('mode').get_default(),
		'matchmaking': MatchChoice._meta.get_field('matchmaking').get_default(),
	}
	return MatchChoice.objects.get_or_create(**defaults)[0]


def get_default_match_choice_id():
	return get_default_match_choice().id


class Match(models.Model):
	date = models.DateTimeField(default=timezone.now)
	info = models.ForeignKey('MatchChoice', related_name="matches", default=get_default_match_choice_id, on_delete=models.CASCADE)
	teams = models.ManyToManyField('Team', related_name="matches")

	def __str__(self):
		return f"Match {self.id} on {self.date}"

	def __repr__(self):
		return self.__str__()


class MatchFilter(django_filters.FilterSet):
	user_id = django_filters.NumberFilter(field_name="teams__players__id")
	username = django_filters.CharFilter(field_name="teams__players__username")
	date = django_filters.DateFilter(field_name="date", lookup_expr="exact")
	date_range = django_filters.DateFromToRangeFilter(field_name="date")
	connectivity = MatchChoiceFilter.declared_filters['connectivity']
	mode = MatchChoiceFilter.declared_filters['mode']
	matchmaking = MatchChoiceFilter.declared_filters['matchmaking']
	win = django_filters.BooleanFilter(method="filter_by_win")

	class Meta:
		model = Match
		fields = ['user_id', 'username', 'date', 'date_range', 'connectivity', 'mode', 'matchmaking', 'win']

	def filter_by_win(self, queryset, name, value):
		user = self.request.user
		if not user.is_authenticated:
			return queryset.none()
		user_teams = Team.objects.filter(user=user)
		if value in (True, False) :
			winning_match_ids = [team.match.id for team in user_teams if team.is_winner() == value]
			return queryset.filter(id__in=winning_match_ids)
		return queryset


class Team(models.Model):
	players = models.ManyToManyField(User, through="Entry")
	score = models.IntegerField(default=0)
	#matches = models.ManyToManyField(Match, related_name="teams") (relation inverse)

	def __str__(self):
		return f"Team {self.id}"

	def __repr__(self):
		return self.__str__()
	
	def is_winner(self):
		return self.score == max([team.score for team in self.match.teams])


class Entry(models.Model):
	user = models.ForeignKey(User, related_name="history", on_delete=models.CASCADE)
	team = models.ForeignKey(Team, related_name="history", on_delete=models.CASCADE)
	pseudo = models.CharField(max_length=20)
	score = models.IntegerField(default=0)

	def __str__(self):
		return f"Player {self.pseudo} in team {self.team.id}: score {self.score}"

	def __repr__(self):
		return self.__str__()
	
	def is_winner(self):
		return self.team.is_winner()


# ********************************************* REDIS ORM MODELS *********************************************


class WaitingLobby(rom.Model):
	lobby = rom.OneToOne("Lobby", on_delete="set null")
	start = rom.DateTime(default=datetime.now())
	matchmaking = rom.ManyToOne("Matchmaking", on_delete="cascade")

	@classmethod
	def get_or_create(cls, lobby, matchmaking=None):
		waiting_lobbies = cls.query.all()
		for waiting_lobby in waiting_lobbies :
			if waiting_lobby.lobby and waiting_lobby.lobby.id == lobby.id :
				if matchmaking and (not waiting_lobby.matchmaking or waiting_lobby.matchmaking.id != matchmaking.id) :
					waiting_lobby.matchmaking = matchmaking
					waiting_lobby.save()
				return waiting_lobby
		if matchmaking:
			waiting_lobby = cls(lobby=lobby, matchmaking=matchmaking)
		else:
			waiting_lobby = cls(lobby=lobby)
		waiting_lobby.save()
		return waiting_lobby
	
	@classmethod
	def get_by_lobby(cls, lobby):
		waiting_lobbies = cls.query.all()
		for waiting_lobby in waiting_lobbies :
			if waiting_lobby.lobby and waiting_lobby.lobby.id == lobby.id :
				return waiting_lobby
	
	def __str__(self) :
		return f"<WLobby {self.lobby.id}(start:{self.start})>"
	
	def get_queue_time(self):
		time_difference = datetime.now() - self.start
		return time_difference.total_seconds()
	
	def add_to_queue(self, matchmaking):
		if not self.matchmaking or self.matchmaking.id != matchmaking.id:
			self.matchmaking = matchmaking
		self.start = datetime.now()
		self.save()
	
	def remove_from_queue(self):
		self.matchmaking = None
		self.save()
	

class Matchmaking(rom.Model) :
	match_choice = rom.ForeignModel(MatchChoice)
	queue = rom.OneToMany("WaitingLobby")

	@classmethod
	def get_by_match_choice(cls, match_choice):
		matchmakings = cls.query.all()
		for matchmaking in matchmakings:
			if matchmaking.match_choice.id == match_choice.id :
				return matchmaking
			
	@classmethod
	def get_or_create(cls, match_choice):
		matchmaking = cls.get_by_match_choice(match_choice)
		if not matchmaking:
			matchmaking = cls(match_choice=match_choice)
			matchmaking.save()
		return matchmaking
	
	def __str__(self) :
		return f"<MM {self.match_choice}: {self.queue}>"
	

class LobbyRequest(rom.Model):
	id = rom.PrimaryKey(index=True)
	recipient = rom.ManyToOne("LobbyPlayer", on_delete="cascade")
	_sender = rom.String()
	_type = rom.String()

	@property
	def type(self):
		if self._type:
			return self._type.decode('utf-8')
	
	@property
	def sender(self):
		user = User.objects.get(username=self._sender.decode('utf-8'))
		if user:
			return LobbyPlayer.get_by_user(user)
	
	@type.setter
	def type(self, value):
		if value:
			self._type = value.encode('utf-8')

	@sender.setter
	def sender(self, value):
		if self._sender:
			self._sender = value.user.username.encode('utf-8')


class WebsocketStatus():
	DISCONNECTED = 0
	CONNECTING = 1
	CONNECTED = 2
	DISCONNECTING = 3


class LobbyChange():
	MATCH_CHOICE = "match-choice"
	LEAVE = "leave"
	JOIN = "join"
	LOBBY_REQUEST = "lobby-request"
	LOBBY = "lobby"
	MATCHMAKING = "matchmaking"
	PLAYER = "player"


class LobbyPlayer(rom.Model) :
	user = rom.ForeignModel(User)
	_pseudo = rom.String()
	is_ready = rom.Boolean(default=True)
	is_leader = rom.Boolean(default=True)
	lobby = rom.OneToOne("Lobby", on_delete="set null")
	requests = rom.OneToMany("LobbyRequest")
	ws_status = rom.Integer(default=WebsocketStatus.DISCONNECTED)

	@property
	def pseudo(self):
		if self._pseudo:
			return self._pseudo.decode('utf-8')
	
	@pseudo.setter
	def pseudo(self, value):
		if value:
			self._pseudo = value.encode('utf-8')

	@classmethod
	def get_by_user(cls, user):
		lobby_players = cls.query.all()
		for lobby_player in lobby_players:
			if lobby_player.user.id == user.id :
				return lobby_player

	@classmethod
	def get_or_create(cls, user, lobby=None):
		lobby_player = cls.get_by_user(user)
		if lobby_player :
			if lobby and not lobby_player.lobby:
				lobby_player.join_lobby(lobby)
			return lobby_player
		lobby_player = cls(user=user, lobby=lobby, _pseudo=user.get_pseudo())
		lobby_player.save()
		return lobby_player
	
	def change_leadership(self, change):
		self.is_leader = change
		self.is_ready = change
		self.save()

	def join_lobby(self, lobby=None) :
		self.requests.clear()
		if lobby:
			self.lobby = lobby
			self.change_leadership(False)
		else:
			self.lobby = Lobby()
			self.change_leadership(True)
		logger.info(f"[LobbyPlayer{self.id}] : JOINED LOBBY {self.lobby.id}")

	def leave_lobby(self) :
		new_leader = None
		logger.info(f"[LobbyPlayer{self.id}] : LEAVING LOBBY {self.lobby.id}")
		if len(self.lobby.members) <= 1 :
			logger.info(f"[LobbyPlayer{self.id}] : DELETING EMPTY LOBBY {self.lobby.id}")
			self.lobby.delete()
		elif self.is_leader :
			for player in self.lobby.members :
				if player.id != self.id :
					player.change_leadership(True)
					logger.info(f"[LobbyPlayer{self.id}] : Leadership of lobby {self.lobby.id} passed to {player.user.username}")
					new_leader = player
					break
		self.lobby = None
		self.save()
		return new_leader

	def change_lobby(self, lobby):
		new_leader = self.leave_lobby()
		self.join_lobby(lobby)
		return new_leader


class Lobby(rom.Model) :
	id = rom.PrimaryKey(index=True)
	members = rom.OneToMany("LobbyPlayer")
	match_choice = rom.ForeignModel(MatchChoice, default=get_default_match_choice)
	is_open = rom.Boolean(default=False)
	is_in_queue = rom.Boolean(default=False)

	@classmethod
	def get_by_user(cls, user):
		lobby_player = LobbyPlayer.get_by_user(user)
		if lobby_player :
			return lobby_player.lobby

	@classmethod
	def get_or_create(cls, user):
		lobby_player = LobbyPlayer.get_or_create(user)
		if lobby_player.lobby:
			return lobby_player.lobby
		lobby_player.join_lobby()
		return lobby_player.lobby
	
	@property
	def all_ready(self):
		return all(player.is_ready for player in self.members)
	
	def add_player(self, user) :
		player = LobbyPlayer.get_or_create(user)
		player.join_lobby(self)

	def remove_player(self, user):
		player = LobbyPlayer.get_by_user(user)
		if player:
			player.leave_lobby(self)

	def is_leader(self, user) :
		lobby_player = LobbyPlayer.get_by_user(user)
		if lobby_player and lobby_player.lobby and lobby_player.lobby.id == self.id:
			return lobby_player.is_leader
		return False
	
	def get_leader(self):
		for member in self.members.all():
			if member.is_leader :
				return member

	def is_allowed_for(self, user):
		if self.is_open :
			return True
		for member in self.members:
			if user.is_friend_with(member.user):
				return True
		return False
	
	def get_queue_time(self):
		waiting_lobby = WaitingLobby.get_by_lobby(self)
		if waiting_lobby:
			return waiting_lobby.get_queue_time()
		return 0