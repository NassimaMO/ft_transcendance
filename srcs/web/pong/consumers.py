import json, logging, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from asgiref.sync import sync_to_async # type: ignore
from .models import *
from .serializers import PongGameStateSerializer

logger = logging.getLogger('default')

class PongConsumer(AsyncWebsocketConsumer):
    STATE_DELAY = 0.001
    START_TIMEOUT = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.match = None
        self.match_id  = None
        self.team = None
        self.session = None
        self.running = asyncio.Event()
        self.generate_handlers(['game_state'])

    def generate_handlers(self, event_types):
        for event_type in event_types:
            async def handler(self, event):
                # await self.logger(event)
                await self.send(text_data=json.dumps(event))
            setattr(self, event_type, handler.__get__(self))   

    async def connect(self):
        self.user = self.scope['user']
        if not self.user:
            self.logger("Unauthorized action : Invalid user.", logger.error)
            return await self.close(1008, reason="Invalid user")
        if not self.user.is_authenticated:
            self.logger("Unauthorized action : User not authenticated.", logger.error)
            return await self.close(1008, reason="User not authenticated")
        self.match_id = self.scope['url_route']['kwargs']['game_id']
        self.match = await sync_to_async(Match.objects.get)(id=self.match_id)
        if not self.match:
            self.logger("Unauthorized action : Invalid match.", logger.error)
            return await self.close(1008, reason="Invalid match")
        self.team = await sync_to_async(self.match.get_team)(self.user)
        if not self.team:
            self.logger("Unauthorized action : You are not in that match.", logger.error)
            return await self.close(1008, reason="Invalid player")
        self.session = await sync_to_async(PongGameSession.get_or_create)(self.match.id)
        await self.add_to_group(await self.get_group_name("session"))
        await self.add_to_group(await self.get_group_name("team"))
        await self.accept()
        asyncio.create_task(self.wait_client())

    async def wait_client(self):
        await self.logger("Waiting for client signal...")
        await asyncio.sleep(self.START_TIMEOUT)
        if not self.running.is_set():
            await self.logger("Timeout expired ; Initiating game.")
            asyncio.create_task(self.game())

    async def start(self, event):
        await self.logger("Received API start signal.")
        if not self.running.is_set():
            await self.logger("Starting Game.")
            asyncio.create_task(self.game())
        else:
            await self.logger("ERROR: Ignoring start signal: Game has already started.", logger_level=logger.error)

    async def disconnect(self, close_code):
        await self.remove_from_group(await self.get_group_name("session"))
        await self.remove_from_group(await self.get_group_name("team"))
        self.running.clear()

    async def logger(self, message, logger_level=logger.info):
        s = "[PongConsumer]"
        group_1 = await self.get_group_name('session')
        if group_1:
            s += f"[{group_1}]"
        group_2 = await self.get_group_name('team')
        if group_2:
            s += f"[{group_2}]"
        s += f" : {message}"
        logger_level(s)

    async def get_group_name(self, group):
        if group == 'session' and self.session:
            return f"pong_session_{self.session.id}"
        if group == 'team' and self.team:
            return f"pong_team_{self.team.id}"
        
    async def add_to_group(self, group):
        if group:
            await self.channel_layer.group_add(
                group, 
                self.channel_name
            )

    async def remove_from_group(self, group):
        if group:
            await self.channel_layer.group_discard(
                group, 
                self.channel_name
            )

    async def game(self):
        self.running.set()
        while self.running.is_set():
            await sync_to_async(self.session.update_state)()
            await self.send_game_state()
            await asyncio.sleep(self.STATE_DELAY)

    def get_game_state(self):
        return PongGameStateSerializer(instance=self.session).data

    async def send_game_state(self):
        await self.channel_layer.group_send(
            await self.get_group_name('session'),
            {
                'type': 'game_state',
                'state': await sync_to_async(self.get_game_state)()
            }
        )

    """ async def move_paddle(self, data):
        player = data['player']
        new_position = data['position']

        await self.update_player_position(player, new_position)

    @database_sync_to_async
    def update_player_position(self, player, new_position):
        game = PongGameSession.objects.get(id=self.game_id)
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
        game = PongGameSession.objects.get(id=self.game_id)
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
        game = PongGameSession.objects.get(id=self.game_id)
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
