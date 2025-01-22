import logging
import json
import rom # type: ignore
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from rest_framework.test import APIRequestFactory # type: ignore
from asgiref.sync import sync_to_async # type: ignore
from . import models
from account.models import Status
# from api.lobby.views import UserLobbiesMainView
# from api.user.views import UserMeView
from api.utils import leave_lobby_api, notify_friends_api
from matchmaker.models import WebsocketStatus, LobbyChange

logger = logging.getLogger("default")

RELOAD_TIMEOUT = 1

# rom.util.use_rom_session()

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
        
    async def add_to_group(self, group):
        group_name = await sync_to_async(self.get_group_name)(group)
        if group_name:
            await self.channel_layer.group_add(
                group_name, 
                self.channel_name
            )

    async def remove_from_group(self, group):
        group_name = await sync_to_async(self.get_group_name)(group)
        if group_name:
            await self.channel_layer.group_discard(
                group_name, 
                self.channel_name
            )

    async def connect(self):
        # rom.util.use_null_session()
        self.waiting_lobby = None
        self.lobby = None
        self.user = self.scope['user']
        if not self.user:
            self.logger("Invalid user", logger.error)
            return await self.close()
        if not self.user.is_authenticated:
            self.logger("User not authenticated", logger.error)
            return await self.close()
        self.add_to_group("user")
        self.lobby = await sync_to_async(models.Lobby.get_by_user)(self.user)
        if not self.lobby:
            self.logger("Unauthorized action : you are not in a lobby", logger.error)
            return self.close()
        self.add_to_group("lobby")
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
        self.remove_from_group("user")
        self.remove_from_group("lobby")
        # rom.util.use_rom_session()


class LobbyConsumer(AsyncWebsocketConsumer):

    def __init__(self) :
        super().__init__()
        self.user = None
        self.player = None
        self.lock = asyncio.Lock()

    def logger(self, message, logger_level=logger.info):
        s = "[LobbyConsumer]"
        if self.player:
            s += f"[{self.get_group_name('player')}]"
            if self.player.lobby:
                s += f"[{self.get_group_name('lobby')}]"
        s += f" : {message}"
        logger_level(s)

    def get_group_name(self, group, id=None) :
        if group == 'player' and self.player:
            if id:
                return f"lobby_player_{id}"
            return f"lobby_player_{self.player.id}"
        if group == 'lobby' and self.player and self.player.lobby:
            if id:
                return f"lobby_{id}"
            return f"lobby_{self.player.lobby.id}"
        
    async def add_to_group(self, group, id=None):
        group_name = await sync_to_async(self.get_group_name)(group, id)
        if group_name:
            await self.channel_layer.group_add(
                group_name, 
                self.channel_name
            )
            # self.logger(f"Added to group: {group_name}")

    async def remove_from_group(self, group):
        group_name = await sync_to_async(self.get_group_name)(group)
        if group_name:
            await self.channel_layer.group_discard(
                group_name, 
                self.channel_name
            )
            # self.logger(f"Removed from group: {group_name}")

    async def connect(self):
        rom.util.use_null_session()
        self.user = self.scope['user']
        await sync_to_async(self.user.refresh_from_db)()
        if not self.user.is_authenticated:
            self.logger("Refusing Connection: User not authenticated", logger.error)
            return await self.close(1003)
        self.player = await sync_to_async(models.LobbyPlayer.get_by_user)(self.user)
        if not self.player or not self.player.lobby:
            self.logger("Unauthorized action : you are not in a lobby", logger.error)
            return self.close(1008)
        await self.add_to_group("player") 
        await self.add_to_group("lobby")
        self.player.ws_status = WebsocketStatus.CONNECTED
        await sync_to_async(self.player.save)()
        # self.logger()
        if self.user.status == Status.OFF:
            await self.change_status(Status.ON)
        # else:
        #     logger.info(f"STATUS != OFF. DIFF : {self.user.status} - {Status.OFF}")
        await self.accept()
        self.logger("Connection accepted")

    async def remove_from_lobby(self):
        # factory = APIRequestFactory()
        # request = factory.delete("users/me/lobbies/main/", {})
        # request.user = self.user
        # view = UserLobbiesMainView.as_view()
        # await sync_to_async(view)(request)
        await sync_to_async(leave_lobby_api)(self.player, back_to_main_lobby=False)
        await sync_to_async(self.player.refresh)(force=True)

    async def change_status(self, status):
        # factory = APIRequestFactory()
        # request = factory.patch("users/me/", {'status': status})
        # request.user = self.user
        # view = UserMeView.as_view()
        # await sync_to_async(view)(request)
        # self.logger("CHANGING STATUS")
        self.user.status = status
        await sync_to_async(self.user.save)()
        await sync_to_async(notify_friends_api)(self.user)
        # self.logger("STATUS CHANGED")

    async def disconnect(self, close_code):
        # rom.util.use_rom_session()
        await self.remove_from_group("player")
        await self.remove_from_group("lobby")
        self.player.ws_status = self.player.ws_status = WebsocketStatus.DISCONNECTED
        await sync_to_async(self.player.save)()
        if close_code == 1001 :
            await asyncio.sleep(RELOAD_TIMEOUT)
            await sync_to_async(self.player.refresh)(force=True)
            if self.player.ws_status == WebsocketStatus.CONNECTED:
                self.logger("Reload")
            else:
                self.logger("Disconnection")
                if self.player.lobby:
                    await self.remove_from_lobby()
                await self.change_status(Status.OFF)
        else:
            await sync_to_async(self.player.refresh)(force=True)
            if self.player.lobby:
                await self.remove_from_lobby()
            await self.change_status(Status.OFF)

    async def api_notif(self, event) :
        self.logger(f"Received API Notif : 'changes': {list(event.get('changes', []))}")
        for change in event.get("changes") :
            if change.get("type") == LobbyChange.LEAVE and change.get("username") == self.user.username:
                await sync_to_async(self.player.refresh)(force=True)
                return await self.remove_from_group("lobby")
            elif change.get("type") == LobbyChange.LOBBY:
                await sync_to_async(self.player.refresh)(force=True)
                await self.add_to_group("lobby")
        await self.send(text_data=json.dumps({
            'type': 'notif',
            'changes': event.get('changes', [])
            }))