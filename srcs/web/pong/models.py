import rom
from account.models import User
from matchmaker.models import Match
from django.db import models


# ********************************************* POSTGRES ORM MODELS *********************************************


class GameRank(models.TextChoices):
    BRONZE = "bronze", "Bronze"
    SILVER = "silver", "Silver"
    GOLD = "gold", "Gold"
    PLAT = "platinium", "Platinium"
    DIAM = "diamond", "Diamond"
    MASTER = "master", "Master"

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
    def next_rank(cls, current_rank):
        ranks = cls.sorted_ranks()
        try:
            current_index = ranks.index(current_rank)
            if current_index < len(ranks) - 1:
                return ranks[current_index + 1]
            else:
                return current_rank
        except ValueError:
            return None
        

    @classmethod
    def previous_rank(cls, current_rank):
        ranks = cls.sorted_ranks()
        try:
            current_index = ranks.index(current_rank)
            if current_index > 0 :
                return ranks[current_index - 1]
            else:
                return current_rank
        except ValueError:
            return None
    
    @classmethod
    def marks_per_rank(cls):
        return {
            cls.BRONZE: 2,
            cls.SILVER: 3,
            cls.GOLD: 4,
            cls.PLAT: 5,
            cls.DIAM: 10,
            cls.MASTER: 20,
        }
    

class UserRank(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rank = models.CharField(max_length=11, choices=GameRank.choices, default=GameRank.BRONZE)
    division = models.IntegerField(default=4)
    mark = models.IntegerField(default=0)

    def promote(self) :
        if (self.mark == GameRank.marks_per_rank()[self.rank]) :
            if (self.division == 1) :
                if (self.rank != GameRank.sorted_ranks()[-1]) :
                    self.division = 4
                    self.mark = 0
                self.rank = GameRank.next_rank(self.rank)
            else :
                self.division -= 1
                self.mark = 0
        else :
            self.mark += 1
        self.save()

    def demote(self) :
        if (self.mark == 0) :
            if (self.division == 4) :
                if (self.rank != GameRank.sorted_ranks()[0]) :
                    self.division = 1
                    self.mark = GameRank.marks_per_rank()[self.rank]
                self.rank = GameRank.previous_rank(self.rank)
            else:
                self.division += 1
                self.mark = GameRank.marks_per_rank()[self.rank]
        else :
            self.mark -= 1
        self.save()


# ********************************************* REDIS ORM MODELS *********************************************

class Ball(rom.Model):
    position_x = rom.Float(default=0)
    position_y = rom.Float(default=0)
    velocity_x = rom.Float(default=1)
    velocity_y = rom.Float(default=1)

    def reset(self):
        self.position_x = 0
        self.position_y = 0
        self.velocity_x = 1
        self.velocity_y = 1

    def update(self):
        self.position_x += self.velocity_x
        self.position_y += self.velocity_y
        if self.position_y >= 120 or self.position_y <= -120:
            self.velocity_y *= -1

    def __str__(self):
        return f'Ball at ({self.position_x}, {self.position_y}) with velocity ({self.velocity_x}, {self.velocity_y})'


class GameSession(rom.Model):
    match = rom.ForeignModel(Match, required=True)
    ball = rom.OneToOne("Ball", on_delete='cascade')
    player_sessions = rom.OneToMany('PlayerSession')

    @classmethod
    def create(cls, match_id) :
        ball = Ball()
        ball.save()
        game_session = cls(ball=ball, match=match_id)
        game_session.save()
        return game_session
    
    @classmethod
    def get_or_create(cls, match_id):
        session = cls.query.filter(match=match_id).first()
        if not session:
            session = cls.create(match_id)
            session.save()
        return session

    def add_player(self, player_id, field_position) :
        existing_player = PlayerSession.query.filter_by(game_session=self, player_id=player_id).first()
        if existing_player:
            raise ValueError(f"Existing player")
        player = PlayerSession(game_session=self, player_id=player_id, position=field_position)
        player.save()

    def update_game_state(self):
        ball = self.ball
        ball.update()
        if ball.position_x >= 203:
            self.increase_score(FieldPosition.LEFT)
            ball.reset()
        elif ball.position_x <= -203:
            self.increase_score(FieldPosition.RIGHT)
            ball.reset()
        for player_session in self.player_sessions:
            if player_session.position == FieldPosition.RIGHT:
                if ball.position_x + 3 >= 180 - 5 and \
                   ball.position_y <= player_session.coordinates + 15 and \
                   ball.position_y >= player_session.coordinates - 15:
                    ball.velocity_x *= -1
            elif player_session.position == FieldPosition.LEFT:
                if ball.position_x - 3 <= -180 + 5 and \
                   ball.position_y <= player_session.coordinates + 15 and \
                   ball.position_y >= player_session.coordinates - 15:
                    ball.velocity_x *= -1
        ball.save()
        self.save()

    def increase_score(self, scoring_position):
        if scoring_position == FieldPosition.LEFT:
            for player_session in self.player_sessions:
                if player_session.position == FieldPosition.LEFT:
                    player_session.score += 1
                    player_session.save()
        elif scoring_position == FieldPosition.RIGHT:
            for player_session in self.player_sessions:
                if player_session.position == FieldPosition.RIGHT:
                    player_session.score += 1
                    player_session.save()

    def __str__(self):
        return f'Game {self.id}'


class FieldPosition:
    LEFT = 0
    RIGHT = 1


class PlayerSession(rom.Model):
    game_session = rom.ManyToOne("GameSession", on_delete='cascade')
    user = rom.ForeignModel(User)
    score = rom.Integer(default=0)
    coordinates = rom.Float(default=0)
    position = rom.Integer(default=FieldPosition.LEFT)

    def __str__(self):
        return f'User {self.user.username} in game {self.game_session.id}'