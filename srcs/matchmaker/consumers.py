import json
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime
from .models import Match, GameMode, MatchMaking

class MatchmakingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.redis = redis.StrictRedis(host='redis', port=6379, db=0)
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
        await self.add_to_queue()
        await self.accept()
        await self.matchmaking()
    
    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.remove_from_queue(self.channel_name)

    async def add_to_queue(self) :
        await self.channel_layer.group_add('matchmaking_queue', self.channel_name)
        await self.redis.zadd('matchmaking_queue', {self.channel_name: datetime.now().timestamp()})
        await self.redis.hset(f"user:{self.channel_name}", mapping={'id':self.user.id, 'rank': self.user.rank})

    async def remove_from_queue(self, channel_name) :
        await self.redis.zrem('matchmaking_queue', channel_name)
        await self.redis.delete(f"user:{channel_name}")
        await self.channel_layer.group_discard('matchmaking_queue', channel_name)

    async def matchmaking(self):
        users_list = await self.redis.zrange('matchmaking_queue', 0, -1, withscores=True)
        if len(users_list) >= 2:
            players = list()
            """ for user_id, timestamp in users_list:
                user_info = await self.redis.hgetall(f"user:{user_id.decode('utf-8')}")
                user_info_decoded = {
                    'rank': user_info.get(b'rank', b'unknown').decode('utf-8'),
                }
                # ** insérer vrai algorithme de sélection de joueurs en fonction de leur rang ici ** """
            players.append(users_list[0][0].decode('utf-8'))
            players.append(users_list[1][0].decode('utf-8'))
            
            match = await sync_to_async(Match.objects.create)(mode=GameMode.ONLINE, mm=MatchMaking.UNRANK)
            match_group_name = f'match_{match.id}'

            for channel_name in players :
                await self.remove_from_queue(channel_name)
                await self.channel_layer.group_add(match_group_name, channel_name)

            match_url = f'/match/{match_group_name}/'
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
