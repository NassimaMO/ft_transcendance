import json
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime
from .models import Match, MatchChoice, GameMode, MatchmakingMode, Connecitvity
import logging

logger = logging.getLogger("default")

class MatchmakingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.redis = redis.StrictRedis(host='redis', port=6379, db=0)
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
        self.match_choice_id = self.scope['url_route']['kwargs']['match_choice_id']
        self.match_choice = await sync_to_async(MatchChoice.objects.get)(id=self.match_choice_id)
        await self.add_to_queue()
        await self.accept()
        await self.matchmaking()
    
    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.remove_from_queue(self.channel_name)

    async def add_to_queue(self) :
        await self.channel_layer.group_add('matchmaking_queue', self.channel_name)
        if not await self.redis.zscore('matchmaking_queue', self.channel_name) :
            await self.redis.zadd('matchmaking_queue', {self.channel_name: datetime.now().timestamp()})
        if not await self.redis.hget(f"user:{self.channel_name}", 'id') :
            await self.redis.hset(f"user:{self.channel_name}", mapping={'id':self.user.id, 'rank': self.user.rank})

    async def remove_from_queue(self, channel_name) :
        await self.redis.zrem('matchmaking_queue', channel_name)
        await self.redis.delete(f"user:{channel_name}")
        await self.channel_layer.group_discard('matchmaking_queue', channel_name)

    async def time_algo(self):
        users_list = await self.redis.zrange('matchmaking_queue', 0, -1, withscores=True)
        players = None
        if len(users_list) >= 2:
            players = list()
            players.append(users_list[0][0].decode('utf-8'))
            players.append(users_list[1][0].decode('utf-8'))
        return players
    
    async def rank_algo(self) :
        pass
        """ for user_id, timestamp in users_list:
                user_info = await self.redis.hgetall(f"user:{user_id.decode('utf-8')}")
                user_info_decoded = {
                    'rank': user_info.get(b'rank', b'unknown').decode('utf-8'),
                }
                # ** insérer vrai algorithme de sélection de joueurs en fonction de leur rang ici ** """

    async def matchmaking(self):
        players = await self.time_algo()
        if (players) :
            match = await sync_to_async(Match.objects.create)(info=self.match_choice)
            match_group_name = f'match_{match.id}'
            for channel_name in players :
                await self.remove_from_queue(channel_name)
                await self.channel_layer.group_add(match_group_name, channel_name)

            match_url = f'/play/game/{match.id}/'
            await self.channel_layer.group_send(
                match_group_name,
                {
                    'type': 'match_found',
                    'match_url': match_url
                }
            )

    async def match_found(self, event):
        match_url = event.get('match_url', None)
        if match_url:
            await self.send(text_data=json.dumps({
                'type': 'match_found',
                'match_url': match_url
            }))
        self.close()

class TournamentConsumer(AsyncWebsocketConsumer):
    pass