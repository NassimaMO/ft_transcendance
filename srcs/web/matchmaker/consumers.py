import redis.asyncio as redis
import logging
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Match, MatchChoice, Channel, WaitingUser, Matchmaking

logger = logging.getLogger("default")

class MatchmakingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.redis = redis.StrictRedis(host='redis', port=6379, db=0)
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            logger.debug("User not authenticated")
            await self.close()
        self.channel = await sync_to_async(Channel.get_or_create)(self.user, self.channel_name)
        self.match_choice = await sync_to_async(MatchChoice.objects.get)(id=self.scope['url_route']['kwargs']['match_choice_id'])
        await sync_to_async(self.add_to_queue)()
        await self.accept()
        await self.create_match()

    def add_to_queue(self):
        self.matchmaking = Matchmaking.get_or_create(mm=self.match_choice.mm)
        self.matchmaking.save()
        self.waiting_user = WaitingUser.get_or_create(self.channel, self.matchmaking)
        self.waiting_user.save()

    def remove_from_queue(self):
        if self.waiting_user :
            self.waiting_user.delete()
        self.waiting_user = None

    def time_algo(self):
        players = None
        if len(self.matchmaking.queue) >= 2:
            players = [waiting_user for waiting_user in self.matchmaking.queue[:2]]
        return players

    async def create_match(self):
        players = await sync_to_async(self.time_algo)()
        if (players) :
            await sync_to_async(self.remove_from_queue)()
            match = await sync_to_async(Match.objects.create)(info=self.match_choice)
            match_group_name = f'match_{match.id}'
            for player in players :
                await self.channel_layer.group_add(match_group_name, player.channel.name.decode('utf-8'))
            match_url = f'/play/game/{match.id}/'
            await self.channel_layer.group_send(
                match_group_name,
                {
                    'type': 'match_found',
                    'match_url': match_url
                }
            )

    async def match_found(self, event):
        if self.waiting_user :
            await sync_to_async(self.remove_from_queue)()
        match_url = event.get('match_url', None)
        if match_url:
            await self.send(text_data=json.dumps({
                'type': 'match_found',
                'match_url': match_url
            }))
        self.close()

    async def disconnect(self, close_code):
        if self.waiting_user :
            await sync_to_async(self.remove_from_queue)()