import django_filters
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.timezone import now


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



class UserFilter(django_filters.FilterSet):
	status = django_filters.CharFilter(lookup_expr='iexact')

	class Meta:
		model = User
		fields = ['status']


class Session(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_sessions")
	ip_address = models.GenericIPAddressField(null=True, blank=True)
	user_agent = models.CharField(max_length=255, null=True, blank=True)
	login_time = models.DateTimeField(default=now)