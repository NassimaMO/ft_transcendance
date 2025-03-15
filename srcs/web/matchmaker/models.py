import rom
import redis # type: ignore
import django_filters # type: ignore
import logging
import time
import threading
from django.db import models # type: ignore
from django.utils import timezone # type: ignore
from account.models import User
from datetime import datetime
from asgiref.sync import async_to_sync # type: ignore


logger = logging.getLogger('default')


# ********************************************* POSTGRES ORM MODELS *********************************************

class Game(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.name
	
	@classmethod
	def get_default(cls):
		return cls.objects.first() if cls.objects.exists() else None
	
	@classmethod
	def get_default_id(cls):
		return cls.get_default().id
			

class Rank(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="ranks")
	name = models.CharField(max_length=20)
	order = models.IntegerField()
	marks_required = models.IntegerField(default=0)

	class Meta:
		unique_together = ("game", "name")
		ordering = ["game", "order"]

	def __str__(self):
		return self.name

	def next_rank(self):
		next_rank = Rank.objects.filter(game=self.game, order__gt=self.order).order_by("order").first()
		return next_rank if next_rank else self

	def previous_rank(self):
		prev_rank = Rank.objects.filter(game=self.game, order__lt=self.order).order_by("-order").first()
		return prev_rank if prev_rank else self


class UserRank(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ranks")
	game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="user_ranks")
	rank = models.ForeignKey(Rank, on_delete=models.CASCADE, related_name="user_ranks")
	division = models.IntegerField(default=4)
	marks = models.IntegerField(default=0)

	class Meta:
		unique_together = ("user", "game")

	def __str__(self):
		return f"<UserRank {self.game}: {self.rank} {self.division}>"

	def promote(self):
		if self.marks >= self.rank.marks_required:
			if self.division == 1:
				next_rank = self.rank.next_rank()
				if next_rank != self.rank: 
					self.division = 4
					self.marks = 0
					self.rank = next_rank
			else:
				self.division -= 1
				self.marks = 0
		else:
			self.marks += 1
		self.save()

	def demote(self):
		if self.marks == 0:
			if self.division == 4:
				prev_rank = self.rank.previous_rank()
				if prev_rank != self.rank:
					self.division = 1
					self.marks = prev_rank.marks_required
					self.rank = prev_rank
			else:
				self.division += 1
				self.marks = self.rank.marks_required
		else:
			self.marks -= 1
		self.save()


class ChoiceEnum(models.TextChoices):
	@classmethod
	def to_dict(cls):
		return {mode.name: {"value": mode.value, "label": mode.label} for mode in cls}


class GameMode(ChoiceEnum) :
	SOLO = "Solo", "Un joueur (VS IA)"
	MULTI_1V1 = "1v1", "Multijoueur (1v1)"
	MULTI_2V2 = "2v2", "Multijoueur (2v2)"


class Connectivity(ChoiceEnum) :
	LOCAL = "Local", "Local"
	ONLINE = "En ligne", "En ligne"


class MatchmakingMode(ChoiceEnum) :
	UNRANK = "Non Classé", "Non Classé"
	RANK = "Classé", "Classé"
	TOURNAMENT = "Tournoi", "Tournoi"


class MatchChoice(models.Model):
	game = models.ForeignKey('Game', default=Game.get_default, related_name="matches", on_delete=models.CASCADE)
	connectivity = models.CharField(max_length=20, choices=Connectivity.choices, default=Connectivity.LOCAL)
	mode = models.CharField(max_length=20, choices=GameMode.choices, default=GameMode.SOLO)
	matchmaking = models.CharField(max_length=20, choices=MatchmakingMode.choices, default=MatchmakingMode.UNRANK)

	class Meta:
		unique_together = ('game', 'connectivity', 'mode', 'matchmaking')
	
	@classmethod
	def get(cls, pk):
		try:
			return cls.objects.get(pk=pk)
		except cls.DoesNotExist:
			return None
		
	@classmethod
	def get_default(cls):
		defaults = {
			'game': cls._meta.get_field('game').get_default(),
			'connectivity': cls._meta.get_field('connectivity').get_default(),
			'mode': cls._meta.get_field('mode').get_default(),
			'matchmaking': cls._meta.get_field('matchmaking').get_default(),
		}
		if defaults['game'] is not None:
			defaults['game'] = Game.objects.get(pk=defaults['game'])
		return cls.objects.get_or_create(**defaults)[0]

	@classmethod
	def get_default_id(cls):
		return cls.get_default().id

	def __str__(self):
		return f"<MatchChoice {self.id}: {self.game}-{self.mode}-{self.connectivity}-{self.matchmaking}>"
	
	def __repr__(self):
		return self.__str__()
	
	def need_matchmaking(self) :
		if (self.mode == GameMode.SOLO or self.connectivity == Connectivity.LOCAL) :
			return False
		return True
	
	def players_required(self):
		if self.mode == GameMode.SOLO :
			return 1
		if self.mode == GameMode.MULTI_1V1:
			return 2
		if self.mode == GameMode.MULTI_2V2:
			return 4
		
	def teams_required(self):
		return 2
	
	def players_per_team(self):
		if self.mode == GameMode.SOLO or self.mode == GameMode.MULTI_1V1:
			return 1
		if self.mode == GameMode.MULTI_2V2:
			return 2


class MatchChoiceFilter(django_filters.FilterSet):
	connectivity = django_filters.CharFilter(lookup_expr='iexact')
	mode = django_filters.CharFilter(lookup_expr='iexact')
	matchmaking = django_filters.CharFilter(lookup_expr='iexact')

	class Meta:
		model = MatchChoice
		fields = ['connectivity', 'mode', 'matchmaking']


class Match(models.Model):
	date = models.DateTimeField(default=timezone.now)
	info = models.ForeignKey('MatchChoice', related_name="matches", on_delete=models.CASCADE)

	class Meta:
		ordering = ['-date']

	def __str__(self):
		return f"<Match {self.id}: {self.info}, {self.teams.all()}>"

	def __repr__(self):
		return self.__str__()
	
	@classmethod
	def get(cls, pk):
		try:
			return cls.objects.get(pk=pk)
		except cls.DoesNotExist:
			return None
	
	def is_in_match(self, user):
		return self.teams.filter(entries__player__user=user).exists()
	
	def get_team(self, user):
		return self.teams.filter(entries__player__user=user).first()


class MatchFilter(django_filters.FilterSet):
	user_id = django_filters.NumberFilter(field_name="teams__players__id")
	username = django_filters.CharFilter(field_name="teams__players__username")
	date = django_filters.DateFilter(field_name="date", lookup_expr="exact")
	date_range = django_filters.DateFromToRangeFilter(field_name="date")
	game = django_filters.CharFilter(field_name="info__game__name")
	connectivity = MatchChoiceFilter.declared_filters['connectivity']
	mode = MatchChoiceFilter.declared_filters['mode']
	matchmaking = MatchChoiceFilter.declared_filters['matchmaking']
	win = django_filters.BooleanFilter(method="filter_by_win")

	class Meta:
		model = Match
		fields = ['game', 'user_id', 'username', 'date', 'date_range', 'connectivity', 'mode', 'matchmaking', 'win']

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
	match = models.ForeignKey(Match, related_name='teams', on_delete=models.CASCADE)
	score = models.IntegerField(default=0)

	def __str__(self):
		return f"<Team {self.id}: {self.entries.all()}>"

	def __repr__(self):
		return self.__str__()
	
	def is_winner(self):
		return self.score == max([team.score for team in self.match.teams])



class Player(models.Model):
	user = models.ForeignKey(User, related_name="players", on_delete=models.CASCADE, null=True, blank=True)
	pseudo = models.CharField(max_length=10)

	@classmethod
	def get(cls, pk):
		try:
			return cls.objects.get(pk=pk)
		except cls.DoesNotExist:
			return None


class Entry(models.Model):
	player = models.ForeignKey(Player, related_name='entries', on_delete=models.CASCADE)
	team = models.ForeignKey(Team, related_name='entries', on_delete=models.CASCADE)
	score = models.IntegerField(default=0)

	def __str__(self):
		return f"<Player {self.pseudo}: {self.score}>"

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
	info = rom.ForeignModel(MatchChoice)
	queue = rom.OneToMany("WaitingLobby")

	@classmethod
	def get_by_info(cls, match_choice):
		matchmakings = cls.query.all()
		for matchmaking in matchmakings:
			if matchmaking.info.id == match_choice.id :
				return matchmaking
			
	@classmethod
	def get_or_create(cls, match_choice):
		matchmaking = cls.get_by_info(match_choice)
		if not matchmaking:
			matchmaking = cls(info=match_choice)
			matchmaking.save()
		return matchmaking
	
	def __str__(self) :
		return f"<MM {self.info}: {self.queue}>"
	

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


class BaseCodes():
	@classmethod
	def to_dict(cls):
		return {attr: value for attr, value in cls.__dict__.items() if not attr.startswith("__") and not callable(value)}


class WebsocketStatus(BaseCodes):
	DISCONNECTED = 0
	CONNECTING = 1
	CONNECTED = 2
	DISCONNECTING = 3


class LobbyChange(BaseCodes):
	MATCH_CHOICE = "match-choice"
	LEAVE = "leave"
	JOIN = "join"
	LOBBY_REQUEST = "lobby-request"
	LOBBY = "lobby"
	MATCHMAKING = "matchmaking"
	PLAYER = "player"


class LobbyStatus(BaseCodes):
	DEFAULT = "default"
	START = "start"
	IN_QUEUE = "in_queue"
	REDIRECT = "redirect"
	IN_GAME = "in_game"


class LobbyPlayer(rom.Model) :
	player = rom.ForeignModel(Player)
	is_ready = rom.Boolean(default=True)
	is_leader = rom.Boolean(default=True)
	lobby = rom.OneToOne("Lobby", on_delete="set null")
	requests = rom.OneToMany("LobbyRequest")
	ws_status = rom.Integer(default=WebsocketStatus.DISCONNECTED)

	@property
	def pseudo(self):
		return self.player.pseudo
	
	@property
	def user(self):
		return self.player.user

	@pseudo.setter
	def pseudo(self, value):
		if value:
			self.player.pseudo = value

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
		player, created = Player.objects.get_or_create(user=user, pseudo=user.get_pseudo())
		lobby_player = cls(player=player.id, lobby=lobby)
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
	match_choice = rom.ForeignModel(MatchChoice, default=MatchChoice.get_default)
	auto_fill = rom.Boolean(default=False)
	is_open = rom.Boolean(default=False)
	_status = rom.String(default=LobbyStatus.DEFAULT.encode('utf-8'))

	@property
	def status(self):
		if self._status:
			return self._status.decode('utf-8')
	
	@status.setter
	def status(self, value):
		if value:
			self._status = value.encode('utf-8')

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
	
	def members_count(self, include_autofill=False):
		if include_autofill and self.auto_fill is False:
			return self.match_choice.players_required() / self.match_choice.teams_required() 
		return len(self.members)
		
	def is_complete(self, include_autofill=False):
		return self.members_count(include_autofill) == self.match_choice.players_per_team()