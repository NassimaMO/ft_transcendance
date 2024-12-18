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
	info = models.ForeignKey('MatchChoice', related_name="match_info", default=get_default_match_choice_id, on_delete=models.CASCADE)
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

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lock = threading.Lock()

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
	
	def save(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to save WaitingLobby with ID {self.id}")
			try:
				super().save(*args, **kwargs)
				logger.debug(f"Saved WaitingLobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error saving WaitingLobby: {e}")

	def update(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to update WaitingLobby with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				logger.debug(f"Updated WaitingLobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error updating WaitingLobby: {e}")

	def refresh(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to refresh WaitingLobby with ID {self.id}")
			try:
				super().refresh(*args, **kwargs)
				logger.debug(f"Refreshed WaitingLobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error refreshing WaitingLobby: {e}")

	def delete(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to delete WaitingLobby with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				logger.debug(f"Deleted WaitingLobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error deleting WaitingLobby: {e}")

class Matchmaking(rom.Model) :
	match_choice = rom.ForeignModel(MatchChoice)
	queue = rom.OneToMany("WaitingLobby")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lock = threading.Lock()

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
	
	def save(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to save Matchmaking with ID {self.id}")
			try:
				super().save(*args, **kwargs)
				logger.debug(f"Saved Matchmaking with ID {self.id}")
			except Exception as e:
				logger.error(f"Error saving Matchmaking: {e}")

	def update(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to update Matchmaking with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				logger.debug(f"Updated Matchmaking with ID {self.id}")
			except Exception as e:
				logger.error(f"Error updating Matchmaking: {e}")

	def refresh(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to refresh Matchmaking with ID {self.id}")
			try:
				super().refresh(*args, **kwargs)
				logger.debug(f"Refreshed Matchmaking with ID {self.id}")
			except Exception as e:
				logger.error(f"Error refreshing Matchmaking: {e}")

	def delete(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to delete Matchmaking with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				logger.debug(f"Deleted Matchmaking with ID {self.id}")
			except Exception as e:
				logger.error(f"Error deleting Matchmaking: {e}")

class LobbyRequest(rom.Model):
	recipient = rom.ManyToOne("LobbyPlayer", on_delete="cascade")
	sender = rom.String()
	type = rom.String()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lock = threading.Lock()

	def save(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to save LobbyRequest with ID {self.id}")
			try:
				super().save(*args, **kwargs)
				logger.debug(f"Saved LobbyRequest with ID {self.id}")
			except Exception as e:
				logger.error(f"Error saving LobbyRequest: {e}")

	def update(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to update LobbyRequest with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				logger.debug(f"Updated LobbyRequest with ID {self.id}")
			except Exception as e:
				logger.error(f"Error updating LobbyRequest: {e}")

	def refresh(self, *args, **kwargs):
		with self._lock:
			logger.debug(f"Attempting to refresh LobbyRequest with ID {self.id}")
			try:
				super().refresh(*args, **kwargs)
				logger.debug(f"Refreshed LobbyRequest with ID {self.id}")
			except Exception as e:
				logger.error(f"Error refreshing LobbyRequest: {e}")

	# def delete(self, *args, **kwargs):
	# 	with self._lock:
	# 		logger.debug(f"Attempting to delete LobbyRequest with ID {self.id}")
	# 		try:
	# 			super().delete(*args, **kwargs)
	# 			logger.debug(f"Deleted LobbyRequest with ID {self.id}")
	# 		except Exception as e:
	# 			logger.error(f"Error deleting LobbyRequest: {e}")

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
	pseudo = rom.String()
	is_ready = rom.Boolean(default=True)
	is_leader = rom.Boolean(default=True)
	lobby = rom.OneToOne("Lobby", on_delete="set null")
	requests = rom.OneToMany("LobbyRequest")
	ws_status = rom.Integer(default=WebsocketStatus.DISCONNECTED)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lock = threading.Lock()

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
			if lobby and not lobby_player.lobby:
				lobby_player.join_lobby(lobby)
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
	
	def check_pseudo(self, string):
		try:
			decoded_pseudo = self.pseudo.decode('utf-8')
		except UnicodeDecodeError:
			decoded_pseudo = self.pseudo
		return decoded_pseudo == string
		
	
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

	def save(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to save LobbyPlayer with ID {self.id}")
			try:
				super().save(*args, **kwargs)
				# logger.debug(f"Saved LobbyPlayer with ID {self.id}")
			except Exception as e:
				logger.error(f"Error saving LobbyPlayer: {e}")

	def update(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to update LobbyPlayer with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				# logger.debug(f"Updated LobbyPlayer with ID {self.id}")
			except Exception as e:
				logger.error(f"Error updating LobbyPlayer: {e}")

	def refresh(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to refresh LobbyPlayer with ID {self.id}")
			try:
				super().refresh(*args, **kwargs)
				# logger.debug(f"Refreshed LobbyPlayer with ID {self.id}")
			except Exception as e:
				logger.error(f"Error refreshing LobbyPlayer: {e}")

	def delete(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to delete LobbyPlayer with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				# logger.debug(f"Deleted LobbyPlayer with ID {self.id}")
			except Exception as e:
				logger.error(f"Error deleting LobbyPlayer: {e}")


class Lobby(rom.Model) :
	id = rom.PrimaryKey(index=True)
	members = rom.OneToMany("LobbyPlayer")
	match_choice = rom.ForeignModel(MatchChoice, default=get_default_match_choice)
	is_open = rom.Boolean(default=False)
	is_in_queue = rom.Boolean(default=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lock = threading.Lock()

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
		lobby_player.join_lobby()
		return lobby_player.lobby
	
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
	
	def save(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to save Lobby with ID {self.id}")
			try:
				super().save(*args, **kwargs)
				# logger.debug(f"Saved Lobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error saving Lobby: {e}")

	def update(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to update Lobby with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				# logger.debug(f"Updated Lobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error updating Lobby: {e}")

	def refresh(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to refresh Lobby with ID {self.id}")
			try:
				super().refresh(*args, **kwargs)
				# logger.debug(f"Refreshed Lobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error refreshing Lobby: {e}")

	def delete(self, *args, **kwargs):
		with self._lock:
			# logger.debug(f"Attempting to delete Lobby with ID {self.id}")
			try:
				super().update(*args, **kwargs)
				# logger.debug(f"Deleted Lobby with ID {self.id}")
			except Exception as e:
				logger.error(f"Error deleting Lobby: {e}")