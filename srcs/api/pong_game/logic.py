from .models import GameSession
from django.db.models import F
from django.http import JsonResponse

def updateGameState(game_id):
    try:
        game = GameSession.objects.get(id=game_id)
        game.ball_position_x += game.ball_velocity_x
        game.ball_position_y += game.ball_velocity_y

        if game.ball_position_y >= 120 or game.ball_position_y <= -120:
            game.ball_velocity_y *= -1

        if game.ball_position_x >= 203:
            increment_score(game, 'right')
            resetBall(game)
        elif game.ball_position_x <= -203:
            increment_score(game, 'left')
            resetBall(game)

        if game.ball_position_x + 3 >= 180 - 5 and game.ball_position_y <= game.position_player_two + 15 and game.ball_position_y >= game.position_player_two - 15:
            game.ball_velocity_x *= -1
        if game.ball_position_x - 3 <= -180 + 5 and game.ball_position_y <= game.position_player_one + 15 and game.ball_position_y >= game.position_player_one - 15:
            game.ball_velocity_x *= -1

        for player in game.players.all():
            if is_ball_colliding_with_paddle(game, player):
                game.ball_velocity_x *= -1
                break

        game.save()

        player_sessions = game.players.all()
        response_data = {
            'ball_position_x': game.ball_position_x,
            'ball_position_y': game.ball_position_y,
            'position_player_one': player_sessions.filter(position__lt=0).first().position if player_sessions.filter(position__lt=0).exists() else 0,
            'position_player_two': player_sessions.filter(position__gte=0).first().position if player_sessions.filter(position__gte=0).exists() else 0,
        }

        return JsonResponse(response_data)

    except GameSession.DoesNotExist:
        pass

def resetBall(game):
    game.ball_position_x = 0
    game.ball_position_y = 0
    game.ball_velocity_x *= -1

def increment_score(game, direction):
    if direction == 'right':
        player = game.players.filter(position__gte=0).order_by('position').first()
    else:
        player = game.players.filter(position__lte=0).order_by('-position').first()

    if player:
        player.score = F('score') + 1
        player.save()

def is_ball_colliding_with_paddle(game, player):
    paddle_x = 180 if player.position > 0 else -180
    paddle_y_min = player.position - 15
    paddle_y_max = player.position + 15

    within_y_bounds = paddle_y_min <= game.ball_position_y <= paddle_y_max
    within_x_bounds = (paddle_x - 3 <= game.ball_position_x <= paddle_x + 3)
    
    return within_x_bounds and within_y_bounds