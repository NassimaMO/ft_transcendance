import django_filters # type: ignore
from django.db import models # type: ignore
from django.db.models import F # type: ignore
from django.contrib.auth.models import AbstractUser # type: ignore
from django.utils.timezone import now # type: ignore


class UserChange():
	INFO = "user"
	FRIEND_REQUEST = "friend-request"
	FRIEND = "friend"


class Status(models.TextChoices):
	ON = "En Ligne", "En Ligne"
	OFF = "Hors Ligne", "Hors Ligne"
	IG = "Dans une partie", "Dans une partie"
	INV = "Invisible", "Invisible"
	BUSY = "Occupé", "Occupé"
	LOBBY = "Dans un salon", "Dans un salon"


class User(AbstractUser):
	avatar = models.ImageField(upload_to='', default="static/account/media/default_avatar.png")
	banner = models.ImageField(upload_to='', default="static/account/media/default_banner.jpg")
	status = models.CharField(max_length=15, choices=Status.choices, default=Status.OFF)
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
	
	def is_friend_with(self, user):
		return user in self.friends.all()
	
	# STATS
	
	def ordered_history(self):
		return self.history.annotate(date=F('team__matches__date')).order_by('-date')

	def get_total_games_won(self):
		return sum(int(entry.is_winner()) for entry in self.history.all())
	
	def get_average_score(self):
		all_games_played = self.history.all()
		average_score = sum(entry.score for entry in all_games_played)
		average_score = average_score / len(all_games_played) if len(all_games_played) > 0 else 0
		return average_score
	
	def get_win_streak(self):
		win_streak = 0
		for entry in self.ordered_history():
			if entry.is_winner():
				win_streak += 1
			else:
				break
		return win_streak


class UserFilter(django_filters.FilterSet):
	status = django_filters.CharFilter(lookup_expr='iexact')

	class Meta:
		model = User
		fields = ['status']


class Session(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
	ip_address = models.GenericIPAddressField(null=True, blank=True)
	user_agent = models.CharField(max_length=255, null=True, blank=True)
	login_time = models.DateTimeField(default=now)