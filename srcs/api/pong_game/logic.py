from .models import GameSession

def updateGameState(game_id):
    game = GameSession.objects.get(id=game_id)
    
    game.ball_position_x += game.ball_velocity_x
    game.ball_position_y += game.ball_velocity_y

    if game.ball_position_y >= 1.0 or game.ball_position_y <= -1.0:
        game.ball_velocity_y *= -1

    if (game.ball_position_x <= -0.9 and 
        game.player_one.position - 0.5 <= game.ball_position_y <= game.player_one.position + 0.5):
        game.ball_velocity_x *= -1
    if (game.ball_position_x >= 0.9 and 
        game.player_two_position - 0.5 <= game.ball_position_y <= game.player_two_position + 0.5):
        game.ball_velocity_x *= -1

    if game.ball_position_x >= 1.0:
        game.score_player1 += 1
        resetBall(game)
    elif game.ball_position_x <= -1.0:
        game.score_player2 += 1
        resetBall(game)
    
    game.save()

def resetBall(game):
    game.ball_position_x = 0.0
    game.ball_position_y = 0.0
    game.ball_velocity_x *= -1
    game.ball_velocity_y = 0.05 if game.ball_velocity_y < 0 else -0.05