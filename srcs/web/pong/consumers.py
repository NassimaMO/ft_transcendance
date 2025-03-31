import json, logging, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from asgiref.sync import sync_to_async # type: ignore
from .models import *
from .serializers import PongGameStateSerializer

logger = logging.getLogger('default')

class PongConsumer(AsyncWebsocketConsumer):
	STATE_DELAY = 0.001
	START_TIMEOUT = 5
	IA_DELAY = 1

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = None
		self.match = None
		self.match_id  = None
		self.team = None
		self.session = None
		self.player_session = None
		self.players = None
		self.running = asyncio.Event()
		self.generate_handlers(['game_state'])

	def generate_handlers(self, event_types):
		for event_type in event_types:
			async def handler(self, event):
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
		self.session = await sync_to_async(PongGameSession.get_by_match_id)(self.match.id)
		if not self.session:
			self.logger("Unauthorized action : Invalid session.", logger.error)
			return await self.close(1008, reason="Invalid session")
		await self.add_to_group(await self.get_group_name("session"))
		await self.add_to_group(await self.get_group_name("team"))
		await self.accept()
		asyncio.create_task(self.wait_clients())

	async def start_game(self):
		asyncio.create_task(self.game())
		if not self.players:
			self.players = await sync_to_async(self.session.get_player_sessions)()
		for player_session in self.players:
			if player_session.player.is_ai:
				asyncio.create_task(self.ia(player_session))

	async def check_starting(self):
		if not self.players:
			self.players = await sync_to_async(self.session.get_player_sessions)()
		return any([player.status == PongPlayerStatus.STARTING for player in self.players])

	async def wait_clients(self):
		if not self.check_starting():
			await self.game()
		else:
			await self.logger("Waiting for API start signal...")
			await asyncio.sleep(self.START_TIMEOUT)
			if not self.running.is_set():
				await self.logger("Timeout expired ; Initiating game.")
				await self.start_game()

	async def start(self, event):
		await self.logger("Received API start signal.")

		if not self.running.is_set():
			await self.logger("All clients ready ; Starting Game.")
			await self.start_game()
		else:
			await self.logger("ERROR: Ignoring start signal: Game has already started.", logger_level=logger.error)

	async def disconnect(self, close_code):
		await self.remove_from_group(await self.get_group_name("session"))
		await self.remove_from_group(await self.get_group_name("team"))
		self.player_session = await sync_to_async(PongPlayerSession.get_by_user)(self.user)
		if self.player_session:
			self.player_session.status = PongPlayerStatus.AWAY
			await sync_to_async(self.player_session.save)()
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
		self.player_session = await sync_to_async(PongPlayerSession.get_by_user)(self.user)
		if not self.player_session:
			self.logger("Stoping game ; session is no longer available.", logger.error)
			return await self.close(1008, reason="Session unavailable")
		if self.player_session.status != PongPlayerStatus.PLAYING:
			self.player_session.status = PongPlayerStatus.PLAYING
			await sync_to_async(self.player_session.save)()
		while self.running.is_set():
			await asyncio.sleep(self.STATE_DELAY)
			status =  await sync_to_async(self.session.update_state)()
			if status == PongChange.END:
				self.running.clear()
			await self.send_game_state()
		self.session = await sync_to_async(PongGameSession.get_by_match_id)(self.match.id)
		if self.session and status == PongChange.END:
			await sync_to_async(self.session.save_match)()
			await sync_to_async(self.session.delete)()
			await self.send_match_end()

	def ia_easy(self, player_session):
		self.session.refresh(True)
		if player_session.coordinate_y > self.session.ball.coordinate_y :
			player_session.move = PaddleMove.UP
		elif player_session.coordinate_y + player_session.team_session.paddle_length < self.session.ball.coordinate_y :
			player_session.move = PaddleMove.DOWN
		else:
			player_session.move = PaddleMove.STATIC
		player_session.save()

	def ia_medium(self, player_session):
		self.session.refresh(True)
		if player_session.coordinate_y + player_session.team_session.paddle_length / 2 > self.session.ball.coordinate_y :
			player_session.move = PaddleMove.UP
		elif player_session.coordinate_y + player_session.team_session.paddle_length / 2 < self.session.ball.coordinate_y :
			player_session.move = PaddleMove.DOWN
		elif player_session.coordinate_y > self.session.parameters.field_ratio / 2:
			player_session.move = PaddleMove.UP
		elif player_session.coordinate_y < self.session.parameters.field_ratio / 2:
			player_session.move = PaddleMove.DOWN
		else:
			player_session.move = PaddleMove.STATIC
		player_session.save()

	def ia_hard(self, player_session):
		pass

	async def ia(self, player_session, level="medium"):
		while self.running.is_set():
			await sync_to_async(getattr(self, f"ia_{level}"))(player_session)
			asyncio.sleep(self.IA_DELAY)

	def get_game_state(self):
		return PongGameStateSerializer(instance=self.session).data
	
	async def send_match_end(self):
		winner_team = await sync_to_async(self.match.get_winner_team)()
		await self.send(text_data=json.dumps({
			'type': 'game_end',
			'winner': winner_team.id if winner_team else None,
            'url': '/lobby/'
        }))

	async def send_game_state(self):
		await self.send(text_data=json.dumps(
			{
				'type': 'game_state',
				'state': await sync_to_async(self.get_game_state)()
			}))