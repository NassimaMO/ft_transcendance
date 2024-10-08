import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import *

logger = logging.getLogger('default')

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['game_id']
        self.match_group_name = f'match_{self.match_id}'
        self.session = GameSession.get_or_create(self.match_id)
        self.session.add_player()
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.match_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

    """ async def send_game_state(self):
        game = await self.get_game_state()

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_state',
                'game': game
            }
        ) """

    """ async def move_paddle(self, data):
        player = data['player']
        new_position = data['position']

        await self.update_player_position(player, new_position)

    @database_sync_to_async
    def update_player_position(self, player, new_position):
        game = GameSession.objects.get(id=self.game_id)
        if player == 'one':
            player_session = game.player_sessions.filter(position=0).first()  # Gauche
        else:
            player_session = game.player_sessions.filter(position=1).first()  # Droite
        
        if player_session:
            player_session.coordinates = new_position
            player_session.save()

    async def update_ball(self, data):
        new_x = data['position_x']
        new_y = data['position_y']
        new_velocity_x = data['velocity_x']
        new_velocity_y = data['velocity_y']

        await self.update_ball_position(new_x, new_y, new_velocity_x, new_velocity_y)

    @database_sync_to_async
    def update_ball_position(self, x, y, velocity_x, velocity_y):
        game = GameSession.objects.get(id=self.game_id)
        ball = game.ball
        ball.position_x = x
        ball.position_y = y
        ball.velocity_x = velocity_x
        ball.velocity_y = velocity_y
        ball.save()

    async def send_game_state(self):
        game = await self.get_game_state()

        # Diffuser le nouvel état du jeu à tous les membres de la room
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_state',
                'game': game
            }
        )

    @database_sync_to_async
    def get_game_state(self):
        game = GameSession.objects.get(id=self.game_id)
        ball = game.ball
        player_one = game.player_sessions.filter(position=0).first()  # Joueur à gauche
        player_two = game.player_sessions.filter(position=1).first()  # Joueur à droite

        return {
            'ball': {
                'position_x': ball.position_x,
                'position_y': ball.position_y,
                'velocity_x': ball.velocity_x,
                'velocity_y': ball.velocity_y,
            },
            'player_one': {
                'coordinates': player_one.coordinates,
                'score': player_one.score
            },
            'player_two': {
                'coordinates': player_two.coordinates,
                'score': player_two.score
            }
        }

    async def game_state(self, event):
        game = event['game']

        await self.send(text_data=json.dumps(game)) """
