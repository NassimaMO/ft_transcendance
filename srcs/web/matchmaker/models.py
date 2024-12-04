import rom
import django_filters
import logging
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
	
	@classmethod
	def get(cls, pk):
		try:
			return cls.objects.get(pk=pk)
		except cls.DoesNotExist:
			return None

	def __str__(self):
		return f"{self.mode} - {self.connect} - {self.mm}"
	
	def need_matchmaking(self) :
		if (self.mode == GameMode.SOLO or self.connect == Connecitvity.LOCAL) :
			return False
		return True


class MatchChoiceFilter(django_filters.FilterSet):
	connect = django_filters.CharFilter(lookup_expr='iexact')
	mode = django_filters.CharFilter(lookup_expr='iexact')
	mm = django_filters.CharFilter(lookup_expr='iexact')

	class Meta:
		model = MatchChoice
		fields = ['connect', 'mode', 'mm']


class Match(models.Model):
	date = models.DateTimeField(default=timezone.now)
	info = models.ForeignKey('MatchChoice', related_name="match_info", on_delete=models.CASCADE)
	teams = models.ManyToManyField('Team', related_name="match_team")

	def __str__(self):
		return f"Match {self.id} on {self.date}"

	def __repr__(self):
		return self.__str__()


class MatchFilter(django_filters.FilterSet):
	user_id = django_filters.NumberFilter(field_name="teams__players__id")
	username = django_filters.CharFilter(field_name="teams__players__username")
	date = django_filters.DateFilter(field_name="date", lookup_expr="exact")
	date_range = django_filters.DateFromToRangeFilter(field_name="date")
	connect = MatchChoiceFilter.declared_filters['connect']
	mode = MatchChoiceFilter.declared_filters['mode']
	mm = MatchChoiceFilter.declared_filters['mm']
	win = django_filters.BooleanFilter(method="filter_by_win")

	class Meta:
		model = Match
		fields = ['user_id', 'username', 'date', 'date_range', 'connect', 'mode', 'mm', 'win']

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
	players = models.ManyToManyField(User, through="History")
	match = models.ForeignKey(Match, related_name="team_match", on_delete=models.CASCADE)
	score = models.IntegerField(default=0)

	def __str__(self):
		return f"Team {self.id}"

	def __repr__(self):
		return self.__str__()
	
	def is_winner(self):
		return self.score == max([team.score for team in self.match.teams])


class History(models.Model):
	user = models.ForeignKey(User, related_name="history_user", on_delete=models.CASCADE)
	team = models.ForeignKey(Team, related_name="history_team", on_delete=models.CASCADE)
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
	def get_or_create(cls, lobby, matchmaking):
		waiting_lobbies = cls.query.all()
		for waiting_lobby in waiting_lobbies :
			if waiting_lobby == lobby :
				waiting_lobby.matchmaking = matchmaking
				return waiting_lobby
		waiting_lobby = cls(lobby=lobby, matchmaking=matchmaking)
		waiting_lobby.save()
		return waiting_lobby
	
	def __str__(self) :
		return f"<WLobby {self.lobby.leader}(start:{self.start})>"


class Matchmaking(rom.Model) :
	match_choice = rom.ForeignModel(MatchChoice)
	queue = rom.OneToMany("WaitingLobby")

	@classmethod
	def get_by_match_choice(cls, match_choice):
		matchmakings = cls.query.all()
		for matchmaking in matchmakings:
			if matchmaking.match_choice == match_choice :
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
	recipient = rom.ManyToOne("LobbyPlayer", on_delete="cascade")
	sender = rom.String()
	type = rom.String()


class LobbyPlayer(rom.Model) :
	user = rom.ForeignModel(User)
	pseudo = rom.String()
	is_ready = rom.Boolean(default=True)
	is_leader = rom.Boolean(default=True)
	lobby = rom.OneToOne("Lobby", on_delete="set null")
	requests = rom.OneToMany("LobbyRequest")

	@classmethod
	def get_by_user(cls, user):
		lobby_players = cls.query.all()
		for lobby_player in lobby_players:
			if lobby_player.user == user :
				return lobby_player

	@classmethod
	def get_or_create(cls, user, pseudo=None, lobby=None):
		lobby_player = cls.get_by_user(user)
		if lobby_player :
			return lobby_player
		if not pseudo :
			pseudo=user.get_pseudo()
		lobby_player = cls(user=user, pseudo=pseudo, lobby=lobby)
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
		if len(self.lobby.members) == 1 :
			self.lobby.delete()
		elif self.is_leader :
			for player in self.lobby.members :
				if player != self :
					player.is_leader = True
					player.save()
					break
		self.delete()


class Lobby(rom.Model) :
	id = rom.PrimaryKey(index=True)
	members = rom.OneToMany("LobbyPlayer")
	match_choice = rom.ForeignModel(MatchChoice)
	is_open = rom.Boolean(default=False)
	is_in_queue = rom.Boolean(default=False)

	@property
	def leader(self):
		for member in self.members:
			if member.is_leader :
				return member
		return None

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
		new_lobby = cls()
		new_lobby.save()
		lobby_player.lobby = new_lobby
		lobby_player.save()
		return new_lobby
	
	def add_player(self, user) :
		player = LobbyPlayer.get_or_create(user)
		player.join_lobby(self)

	def remove_player(self, user):
		player = LobbyPlayer.get_or_create(user)
		player.leave_lobby(self)

	def is_leader(self, user) :
		lobby_player = LobbyPlayer.get_by_user(user)
		if lobby_player :
			return lobby_player.is_leader
		return False