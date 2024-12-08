# import redis.asyncio as redis
import logging
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from . import models
from account.models import User
import rom

logger = logging.getLogger("default")
rom.util.use_null_session()

class MatchmakingConsumer(AsyncWebsocketConsumer):

    def logger(self, message, logger_level=logger.info):
        s = "[MatchmakingConsumer]"
        if self.user:
            s+= f"[User{self.user.id}]"
        if self.lobby:
            s += f"[Lobby{self.lobby.id}]"
        s += f" : {message}"
        logger_level(s)

    def get_group_name(self, group):
        if group == 'user' and self.user:
            return f"matchmaking_user_{self.user.id}"
        if group == 'lobby' and self.lobby:
            return f"matchmaking_lobby_{self.lobby.id}"

    async def connect(self):
        self.waiting_lobby = None
        self.lobby = None
        self.user = self.scope['user']
        if not self.user:
            self.logger("Invalid user", logger.error)
            return await self.close()
        self.logger("Connected to websocket")
        if not self.user.is_authenticated:
            self.logger("User not authenticated", logger.error)
            return await self.close()
        await self.channel_layer.group_add(
            await sync_to_async(self.get_group_name)("user"),
            self.channel_name
        )
        self.lobby = await sync_to_async(models.Lobby.get_by_user)(self.user)
        if not self.lobby:
            self.logger("Unauthorized action : you are not in a lobby", logger.error)
            return self.close()
        await self.channel_layer.group_add(
            await sync_to_async(self.get_group_name)("lobby"), 
            self.channel_name
        )
        await self.accept()

    async def start(self, event):
        self.lobby = await sync_to_async(models.Lobby.get_by_user)(self.user)
        if not self.lobby:
            self.logger("Unauthorized action : you are not in a lobby", logger.error)
            return self.close()
        is_leader = await sync_to_async(self.lobby.is_leader)(self.user)
        if not is_leader :
            self.logger("Unauthorized action : you are not the lobby leader", logger.error)
        else:
            self.logger("Matchmaking started")
            self.match_choice = self.lobby.match_choice
            await sync_to_async(self.add_to_queue)()
            await self.create_match()

    def add_to_queue(self):
        self.logger("Client added to queue")
        if not self.lobby.is_in_queue :
            with rom.util.EntityLock(self.lobby, 5, 90):
                self.lobby.update(is_in_queue=True)
        self.matchmaking = models.Matchmaking.get_or_create(self.match_choice)
        self.matchmaking.save()
        self.waiting_lobby = models.WaitingLobby.get_or_create(self.lobby, self.matchmaking)
        self.waiting_lobby.save()

    async def remove_from_queue(self):
        self.logger("Client removed from queue")
        if self.waiting_lobby :
            await sync_to_async(self.waiting_lobby.delete)()
        self.waiting_lobby = None
        if self.lobby.is_in_queue:
            with rom.util.EntityLock(self.lobby, 5, 90):
               await sync_to_async(self.lobby.update)(is_in_queue=True)
    def time_algo(self):
        self.logger("Checking queue")
        lobbies = None
        if len(self.matchmaking.queue) >= 2:
            lobbies = [waiting_lobby.lobby for waiting_lobby in self.matchmaking.queue[:2]]
        return lobbies

    async def create_match(self):
        lobbies = await sync_to_async(self.time_algo)()
        if lobbies :
            self.logger("Creating match")
            await self.remove_from_queue()
            match = await sync_to_async(models.Match.objects.create)(info=self.match_choice)
            match_url = f'/play/game/{match.id}/'
            for lobby in lobbies :
                await self.channel_layer.group_send(
                    f"matchmaking_lobby_{lobby.id}",
                    {
                        'type': 'match_found',
                        'match_url': match_url
                    }
                )

    async def match_found(self, event):
        self.logger("Match found")
        match_url = event.get('match_url', None)
        if match_url:
            await self.send(text_data=json.dumps({
                'type': 'match_found',
                'match_url': match_url
            }))
        self.close()

    async def disconnect(self, close_code):
        self.logger("Disconnected from websocket")
        await self.remove_from_queue()
        user_group_name = await sync_to_async(self.get_group_name)("user")
        if user_group_name:
            await self.channel_layer.group_discard(
                user_group_name,
                self.channel_name
            )
        lobby_group_name = await sync_to_async(self.get_group_name)("lobby")
        if lobby_group_name:
            await self.channel_layer.group_discard(
                lobby_group_name,
                self.channel_name
            )


class LobbyConsumer(AsyncWebsocketConsumer):

    def logger(self, message, logger_level=logger.info):
        s = "[LobbyConsumer]"
        if self.lobby:
            s += f"[Lobby{self.lobby.id}]"
        if self.player:
            s += f"[Player{self.player.id}]"
        s += f" : {message}"
        logger_level(s)

    def get_group_name(self, group) :
        if group == 'player' and self.player:
            return f"lobby_player_{self.player.id}"
        if group == 'lobby' and self.lobby:
            return f"lobby_{self.lobby.id}"

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            self.logger("User not authenticated", logger.error)
            return await self.close()
        self.player = await sync_to_async(models.LobbyPlayer.get_by_user)(self.user)
        if not self.player:
            self.logger("Unauthorized action : you are not in a lobby", logger.error)
            return self.close()
        await self.channel_layer.group_add(
            await sync_to_async(self.get_group_name)("player"), 
            self.channel_name
        )
        self.lobby = await sync_to_async(models.Lobby.get_by_user)(self.user)
        await self.channel_layer.group_add(
            await sync_to_async(self.get_group_name)("lobby"), 
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            await sync_to_async(self.get_group_name)("player"),
            self.channel_name
        )
        await self.channel_layer.group_discard(
            await sync_to_async(self.get_group_name)("lobby"),
            self.channel_name
        )

    async def api_notif(self, event) :
        self.logger("Received API Notif :")
        self.logger(f"'changes': {event['changes']}")
        await self.send(text_data=json.dumps({
            'type': 'notif',
            'changes': event['changes']
            }))
        
rom.util.use_rom_session()