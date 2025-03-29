import rom # type: ignore
import random
import math
from django.db import models # type: ignore
from matchmaker.models import Match, BaseCodes, Player, Entry
from datetime import datetime
import logging

EPS = 1e-9

logger = logging.getLogger('default')

# ********************************************* POSTGRES ORM MODELS *********************************************

class PongRank(models.TextChoices):
	BRONZE = "Bronze", "Bronze"
	SILVER = "Silver", "Silver"
	GOLD = "Gold", "Gold"
	PLAT = "Platinium", "Platinium"
	DIAM = "Diamond", "Diamond"
	MASTER = "Master", "Master"

	@classmethod
	def sorted_ranks(cls):
		return [
			cls.BRONZE,
			cls.SILVER,
			cls.GOLD,
			cls.PLAT,
			cls.DIAM,
			cls.MASTER,
		]

	@classmethod
	def marks_per_rank(cls):
		return {
			cls.BRONZE: 2,
			cls.SILVER: 3,
			cls.GOLD: 5,
			cls.PLAT: 6,
			cls.DIAM: 8,
			cls.MASTER: 10,
		}


# ********************************************* REDIS ORM MODELS *********************************************


class FieldPosition(BaseCodes):
	LEFT = 0
	RIGHT = 1

	@classmethod
	def opposite(cls, position):
		if position == cls.RIGHT:
			return cls.LEFT
		if position == cls.LEFT:
			return cls.RIGHT


class PongParameters(rom.Model):
	ball_radius = rom.Float(default=0.01)
	ball_speed = rom.Float(default=0.5)
	paddle_length = rom.Float(default=0.3)
	paddle_width = rom.Float(default=0.05)
	paddle_gap = rom.Float(default=0.05)
	paddle_speed = rom.Float(default=0.3)
	field_ratio = rom.Float(default=0.5)
	win_score = rom.Integer(default=10)

	@classmethod
	def get_default(cls):
		return cls()


class Ball(rom.Model):
	coordinate_x = rom.Float(default=0.5)
	coordinate_y = rom.Float(default=PongParameters.get_default().field_ratio / 2)
	velocity_x = rom.Float(default=random.choice([-1, 1]))
	velocity_y = rom.Float(default=random.choice([-1, 1]))
	radius = rom.Float(default=PongParameters.get_default().ball_radius)
	speed = rom.Float(default=PongParameters.get_default().ball_speed)
	last_update = rom.DateTime(default=datetime.now())

	def __str__(self):
		return f'<Ball: ({self.coordinate_x}, {self.coordinate_y}) ({self.velocity_x}, {self.velocity_y})>'


class PongChange(BaseCodes):
	BALL = 0
	COLLIDE = 1
	GOAL = 2
	PADDLE = 3
	END = 4


class PongPlayerStatus(BaseCodes):
	STARTING = 0
	WAITING = 1
	PLAYING = 2
	AWAY = 3


class PaddleMove(BaseCodes):
	STATIC = 0
	UP = 1
	DOWN = 2

	@classmethod
	def to_int(cls, value):
		if not value:
			return PaddleMove.STATIC
		return super().to_int(value)

	@classmethod
	def to_string(cls, value):
		if not value:
			return 'static'
		return super().to_string(value)


class PongTeamSession(rom.Model):
	game_session = rom.ManyToOne("PongGameSession", on_delete='cascade')
	field_position = rom.Integer(default=FieldPosition.LEFT, index=True)
	score = rom.Integer(default=0)
	player_sessions = rom.OneToMany('PongPlayerSession')
	paddle_length = rom.Float(default=PongParameters.get_default().paddle_length)
	last_touch = rom.OneToOne('PongPlayerSession', on_delete='cascade')

	def __str__(self):
		return f'<PongTeamSession {self.id}: {self.player_sessions}>'


class PongPlayerSession(rom.Model):
	team_session = rom.ManyToOne("PongTeamSession", on_delete='cascade')
	player = rom.ForeignModel(Player)
	score = rom.Integer(default=0)
	coordinate_y = rom.Float(default=0)
	coordinate_x = rom.Float(default=0)
	move = rom.Integer(default=PaddleMove.STATIC, required=False)
	status = rom.Integer(default=PongPlayerStatus.STARTING)
	last_update = rom.DateTime(default=None, required=False)

	@classmethod
	def get_by_user(cls, user):
		for player_session in cls.query.all():
			if player_session.player.user.id == user.id:
				return player_session

	def __str__(self):
		return f'<PongPlayerSession of {self.player.user.username}>'


class PongGameSession(rom.Model):
	id = rom.PrimaryKey(index=True)
	match = rom.ForeignModel(Match, required=True)
	ball = rom.OneToOne("Ball", on_delete='cascade')
	team_sessions = rom.OneToMany('PongTeamSession')
	parameters = rom.ManyToOne('PongParameters', default=PongParameters.get_default, on_delete='cascade')

	def _position_player(self, player_session, team_session, team_players_count, player_number):
		y = (self.parameters.field_ratio - team_players_count * team_session.paddle_length) / (team_players_count + 1)
		player_session.coordinate_y = y + (team_session.paddle_length + y) * player_number
		if player_session.team_session.field_position == FieldPosition.LEFT:
			player_session.coordinate_x = self.parameters.paddle_gap
		elif player_session.team_session.field_position == FieldPosition.RIGHT:
			player_session.coordinate_x = 1 - self.parameters.paddle_gap - self.parameters.paddle_width
		player_session.save()

	def _create_teams(self):
		for i, team in enumerate(self.match.teams.all()):
			entries = team.entries.all()
			if i % 2 :
				field_position=FieldPosition.RIGHT
			else:
				field_position=FieldPosition.LEFT
			team_session = PongTeamSession(game_session=self, field_position=field_position, 
											paddle_length=self.parameters.paddle_length * self.parameters.field_ratio / len(entries))
			team_session.save()
			for i, entry in enumerate(entries) :
				player_session = PongPlayerSession(team_session=team_session, player=entry.player)
				self._position_player(player_session, team_session, len(entries), i)

	def _generate_angle(self, direction=None, margin_ratio=24):
		margin = 2 * math.pi / margin_ratio
		valid_ranges = [
			(math.pi / 2 + margin, math.pi - margin),
			(math.pi + margin, 3 * math.pi / 2 - margin),
			(3 * math.pi / 2 + margin, 2 * math.pi - margin),
			(margin, math.pi / 2 - margin)
		]
		if direction == FieldPosition.LEFT:
			theta = random.uniform(*random.choice(valid_ranges[:2]))
		elif direction == FieldPosition.RIGHT:
			theta = random.uniform(*random.choice(valid_ranges[2:]))
		else:
			theta = random.uniform(*random.choice(valid_ranges))
		return theta

	def reset_ball(self, direction=None):
		self.ball.coordinate_x = 0.5
		self.ball.coordinate_y = 0.5 * self.parameters.field_ratio
		theta = self._generate_angle(direction=direction)
		self.ball.velocity_x = self.ball.speed * math.cos(theta)
		self.ball.velocity_y = self.ball.speed * math.sin(theta)
		self.ball.last_update = datetime.now()

	@classmethod
	def create(cls, match_id, parameters=PongParameters.get_default()) :
		ball = Ball()
		ball.save()
		game_session = cls(ball=ball, match=Match.objects.get(id=match_id), parameters=parameters)
		game_session._create_teams()
		game_session.reset_ball()
		game_session.ball.save()
		game_session.save()
		return game_session
	
	@classmethod
	def get_by_match_id(cls, match_id):
		sessions = cls.query.all()
		for session in sessions:
			if session.match.id == match_id:
				return session

	@classmethod
	def get_or_create(cls, match_id):
		session = cls.get_by_match_id(match_id)
		if session:
			return session
		session = cls.create(match_id)
		session.save()
		return session
	
	def save_match(self):
		for player_session in self.get_player_sessions():
			entry = Entry.objects.filter(match__id=self.match.id, player__id=player_session.player.id).first()
			entry.score = player_session.score
			entry.team.score = player_session.team.score
			entry.save()

	def get_player_sessions(self):
		return [player for team in self.team_sessions for player in team.player_sessions]

	def check_goal(self):
		if self.ball.coordinate_x < 0:
			return PongTeamSession.query.filter(game_session=self.id, field_position=FieldPosition.RIGHT).all()
		if self.ball.coordinate_x > 1:
			return PongTeamSession.query.filter(game_session=self.id, field_position=FieldPosition.LEFT).all()
	
	def _get_collidables(self):
		collidables = {'x': [], 'y': []}
		if self.ball.velocity_y > 0:
			collidables['y'].append((self.parameters.field_ratio, 0, 1, 'w'))
		if self.ball.velocity_y < 0:
			collidables['y'].append((0, 0, 1, 'w'))
		for team in self.team_sessions:
			if self.ball.velocity_x > 0 and team.field_position == FieldPosition.RIGHT:
				collidables['x'] += [(player.coordinate_x, player.coordinate_y, player.coordinate_y + team.paddle_length, 'p', player) 
								  for player in team.player_sessions if self.ball.coordinate_x <= player.coordinate_x]
			if self.ball.velocity_x < 0 and team.field_position == FieldPosition.LEFT:
				collidables['x'] += [(player.coordinate_x + self.parameters.paddle_width, 
								   player.coordinate_y, 
								   player.coordinate_y + team.paddle_length, 
								   'p', player)
								   for player in team.player_sessions if self.ball.coordinate_x >= player.coordinate_x + self.parameters.paddle_width]
			if self.ball.velocity_y > 0 :
				collidables['y'] += [(player.coordinate_y, player.coordinate_x, player.coordinate_x + self.parameters.paddle_width, 'p', player) 
								  for player in team.player_sessions if self.ball.coordinate_y <= player.coordinate_y]
			if self.ball.velocity_y < 0 :
				collidables['y'] += [(player.coordinate_y + team.paddle_length, 
								   player.coordinate_x, 
								   player.coordinate_x + self.parameters.paddle_width,
								   'p', player) 
									for player in team.player_sessions if self.ball.coordinate_y >= player.coordinate_y + team.paddle_length]
		return collidables

	def update_ball(self):
		now = datetime.now()
		dt = (now - self.ball.last_update).total_seconds()
		if dt > 0.5 :
			dt = 0.5
		px, py = self.ball.coordinate_x, self.ball.coordinate_y
		dx, dy = self.ball.velocity_x * dt, self.ball.velocity_y * dt
		status = PongChange.BALL
		teams_scorer = self.check_goal()
		if teams_scorer is not None:
			self.reset_ball(FieldPosition.opposite(teams_scorer[0].field_position))
			return status
		r = self.ball.radius
		collides = []
		walls = self._get_collidables()
		for wall in walls['x']:
			if dx > 0 and (px + dx + r) >= wall[0]:
				if wall[1] <= py + dy <= wall[2]:
					ax = wall[0] - r - abs((px + dx + r) - wall[0])
					collides.append((abs(wall[0] - px), 'x', ax, *wall[3:]))
			elif dx < 0 and (px + dx - r) <= wall[0]:
				if wall[1] <= py + dy <= wall[2]:
					ax = wall[0] + r + abs(wall[0] - (px + dx - r))
					collides.append((abs(wall[0] - px), 'x', ax, *wall[3:]))
		for wall in walls['y']:
			if dy > 0 and (py + dy + r) >= wall[0]:
				if wall[1] <= px + dx <= wall[2]:
					ay = wall[0] - r - abs((py + dy + r) - wall[0])
					collides.append((abs(wall[0] - py), 'y', ay, *wall[3:]))
			elif dy < 0 and (py + dy - r) <= wall[0]:
				if wall[1] <= px + dx <= wall[2]:
					ay = wall[0] + r + abs(wall[0] - (py + dy - r))
					collides.append((abs(wall[0] - py), 'y', ay, *wall[3:]))
		self.ball.coordinate_x += dx
		self.ball.coordinate_y += dy
		if collides:
			collide_x = min((c for c in collides if c[1] == 'x'), default=None, key=lambda c: c[0])
			collide_y = min((c for c in collides if c[1] == 'y' and (not collide_x or c[0] <= collide_x[0])), default=None, key=lambda c: c[0])
			if collide_x:
				self.ball.coordinate_x = collide_x[2]
				self.ball.velocity_x *= -1 
				if collide_x[3] == 'p':
					scorer = collide_x[4]
					scorer.team_session.last_touch = scorer
					scorer.score += 10
					scorer.save()
					status = PongChange.COLLIDE
			if collide_y:
				self.ball.coordinate_y = collide_y[2]
				self.ball.velocity_y *= -1
				if collide_y[3] == 'p':
					scorer = collide_y[4]
					scorer.team_session.last_touch = scorer
					scorer.score += 10
					scorer.save()
					status = PongChange.COLLIDE
		teams_scorer = self.check_goal()
		if teams_scorer is not None:
			for team_scorer in teams_scorer:
				team_scorer.score += 1
				if team_scorer.score == self.parameters.win_score:
					status = PongChange.END
				if team_scorer.last_touch is not None:
					team_scorer.last_touch.score += 50
					team_scorer.last_touch.save()
					team_scorer.last_touch = None
				team_scorer.save()
			status = PongChange.GOAL
		self.ball.last_update = now
		return status
	
	def update_paddles(self):
		status = None
		for team in self.team_sessions:
			players = team.player_sessions
			for i, player in enumerate(players):
				if player.move != PaddleMove.STATIC:
					now = datetime.now()
					if player.last_update:
						dt = (now - player.last_update).total_seconds()
						if dt > 0.5:
							dt = 0.5
					else:
						dt = 0.001
					if player.move == PaddleMove.UP:
						new_pos = player.coordinate_y - self.parameters.paddle_speed * dt
						if i == 0:
							if new_pos >= 0:
								player.coordinate_y = new_pos
							else:
								player.coordinate_y = 0
						else:
							if new_pos >= players[i - 1].coordinate_y + team.paddle_length:
								player.coordinate_y = new_pos
							else:
								player.coordinate_y = players[i - 1].coordinate_y + team.paddle_length
					if player.move ==PaddleMove.DOWN:
						new_pos = player.coordinate_y + self.parameters.paddle_speed * dt
						n = len(team.player_sessions)
						if i == n - 1:
							if new_pos + team.paddle_length <= self.parameters.field_ratio:
								player.coordinate_y = new_pos
							else:
								player.coordinate_y = self.parameters.field_ratio - team.paddle_length
						else:
							if new_pos + team.paddle_length <= players[i + 1].coordinate_y:
								player.coordinate_y = new_pos
							else:
								player.coordinate_y = players[i + 1].coordinate_y - team.paddle_length
					player.last_update = now
					player.save()
					status = PongChange.PADDLE
				elif player.last_update:
					player.last_update = None
					player.save()
		return status

	def update_state(self):
		status = self.update_ball()
		paddle_status = self.update_paddles() 
		if status == PongChange.BALL and paddle_status == PongChange.PADDLE:
			status = paddle_status
		self.ball.save()
		self.save()
		return status

	def __str__(self):
		return f'<PongGameSession {self.id}: {self.team_sessions}>'