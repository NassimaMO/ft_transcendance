from .models import RegularGameSession

def updateGameState(game_id):
    try:
        game = RegularGameSession.objects.get(id=game_id)
        game.ball_position_x += game.ball_velocity_x
        game.ball_position_y += game.ball_velocity_y

        if game.ball_position_y >= 120 or game.ball_position_y <= -120:
            game.ball_velocity_y *= -1

        if game.ball_position_x >= 203:
            game.score_player_one += 1
            resetBall(game)
        elif game.ball_position_x <= -203:
            game.score_player_two += 1
            resetBall(game)

        if game.ball_position_x + 3 >= 180 - 5 and game.ball_position_y <= game.position_player_two + 15 and game.ball_position_y >= game.position_player_two - 15:
            game.ball_velocity_x *= -1
        if game.ball_position_x - 3 <= -180 + 5 and game.ball_position_y <= game.position_player_one + 15 and game.ball_position_y >= game.position_player_one - 15:
            game.ball_velocity_x *= -1

        game.save()
    except RegularGameSession.DoesNotExist:
        pass

def resetBall(game):
    game.ball_position_x = 0
    game.ball_position_y = 0
    game.ball_velocity_x *= -1