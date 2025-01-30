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
from datetime import datetime

logger = logging.getLogger("default")

RELOAD_TIMEOUT = 1

# rom.util.use_rom_session()

class MatchmakingConsumer(AsyncWebsocketConsumer):

    def logger(self, message, logger_level=logger.info):
        s = "[MatchmakingConsumer]"
        if self.player:
            s += f"[{self.get_group_name('player')}]"
            if self.player.lobby:
                s += f"[{self.get_group_name('lobby')}]"
        s += f" : {message}"
        logger_level(s)

    def get_group_name(self, group):
        if group == 'player' and self.player:
            return f"matchmaking_player_{self.player.id}"
        if group == 'lobby' and self.player.lobby:
            return f"matchmaking_lobby_{self.player.lobby.id}"
        
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
        self.waiting_lobby = None
        self.user = self.scope['user']
        await sync_to_async(self.user.refresh_from_db)()
        if not self.user:
            self.logger("Unauthorized action : Invalid user.", logger.error)
            return await self.close(1008, reason="Invalid user")
        if not self.user.is_authenticated:
            self.logger("Unauthorized action : User not authenticated.", logger.error)
            return await self.close(1008, reason="User not authenticated")
        self.player = await sync_to_async(models.LobbyPlayer.get_by_user)(self.user)
        if not self.player or not self.player.lobby:
            self.logger("Unauthorized action : You are not in a lobby.", logger.error)
            return self.close(1008, reason="You are not in a lobby")
        await self.add_to_group("player") 
        await self.add_to_group("lobby")
        self.player.ws_status = WebsocketStatus.CONNECTED
        await sync_to_async(self.player.save)()
        if self.user.status == Status.OFF:
            await sync_to_async(self.change_status)(Status.ON)
        await self.accept()
        self.logger("Connection accepted")

    def check_all_ready(self):
        return self.player.lobby.all_ready

    async def start(self, event):
        await sync_to_async(self.player.refresh)(force=True)
        if not self.player.lobby:
            self.logger("Unauthorized action : You are not in a lobby.", logger.error)
            return self.close(1008, reason="You are not in a lobby")
        if not self.player.is_leader :
            self.logger("Unauthorized action : You are not the lobby leader.", logger.error)
            return self.close(1008, reason="You are not the lobby leader")
        if not await sync_to_async(self.check_all_ready)():
            self.logger("Unauthorized action : Members not ready.", logger.error)
            return
        self.match_choice = self.player.lobby.match_choice
        await sync_to_async(self.add_to_queue)()
        await self.notify_queue_start()
        await self.create_match()

    async def stop(self, event):
        await sync_to_async(self.player.refresh)(force=True)
        if not self.player.lobby:
            self.logger("Unauthorized action : You are not in a lobby", logger.error)
            return self.close(1008, reason="You are not in a lobby")
        else:
            await sync_to_async(self.remove_from_queue)()
            await self.notify_queue_stop()

    def add_to_queue(self):
        if not self.player.lobby.is_in_queue :
            with rom.util.EntityLock(self.player.lobby, 5, 90):
                self.player.lobby.update(is_in_queue=True)
        self.matchmaking = models.Matchmaking.get_or_create(self.match_choice)
        self.waiting_lobby = models.WaitingLobby.get_or_create(self.player.lobby)
        self.waiting_lobby.add_to_queue(self.matchmaking)
        self.logger("Lobby added to queue")

    def remove_from_queue(self):
        if self.waiting_lobby :
            self.waiting_lobby.delete()
        self.waiting_lobby = None
        if self.player.lobby.is_in_queue:
            with rom.util.EntityLock(self.player.lobby, 5, 90):
               self.player.lobby.update(is_in_queue=False)
        self.logger("Lobby removed from queue")

    def time_algo(self):
        self.logger("Checking queue")
        lobbies = []
        for waiting_lobby in self.matchmaking.queue:
            if waiting_lobby.lobby:
                lobbies.append(waiting_lobby.lobby)
            else:
                waiting_lobby.matchmaking = None
                waiting_lobby.save()
        if len(lobbies) >= 2:
            return lobbies[:2]

    def get_lobby_members(self):
        return self.player.lobby.members

    async def notify_queue_start(self):
        await self.channel_layer.group_send(
            f"matchmaking_lobby_{self.player.lobby.id}",
            {
                'type': 'queue_start',
            }
        )

    async def notify_queue_stop(self):
        await self.channel_layer.group_send(
            f"matchmaking_lobby_{self.player.lobby.id}",
            {
                'type': 'queue_stop',
            }
        )

    async def create_match(self):
        lobbies = await sync_to_async(self.time_algo)()
        if lobbies :
            self.logger("Creating match")
            await sync_to_async(self.remove_from_queue)()
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

    async def queue_start(self, event):
        self.logger('queue_start')
        await self.send(text_data=json.dumps({
            'type': 'queue_start',
        }))

    async def queue_stop(self, event):
        self.logger('queue_stop')
        await self.send(text_data=json.dumps({
            'type': 'queue_stop',
        }))

    async def disconnect(self, close_code):
        await self.remove_from_group("player")
        await self.remove_from_group("lobby")
        if close_code == 1001 :
            await asyncio.sleep(RELOAD_TIMEOUT)
            await sync_to_async(self.player.refresh)(force=True)
            if self.player.ws_status == WebsocketStatus.CONNECTED:
                self.logger("Reload")
            else:
                self.logger("Disconnection")
                await self.stop({'type': 'stop'})
        else:
            await sync_to_async(self.player.refresh)(force=True)
            await self.stop({'type': 'stop'})

    async def api_notif(self, event) :
        self.logger(f"Received API Notif : 'changes': {list(event.get('changes', []))}")
        for change in event.get("changes") :
            if change.get("type") == LobbyChange.LEAVE:
                await sync_to_async(self.player.refresh)(force=True)
                return await self.remove_from_group("lobby")
            elif change.get("type") == LobbyChange.LOBBY:
                await sync_to_async(self.player.refresh)(force=True)
                return await self.add_to_group("lobby")


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

    async def remove_from_group(self, group):
        group_name = await sync_to_async(self.get_group_name)(group)
        if group_name:
            await self.channel_layer.group_discard(
                group_name, 
                self.channel_name
            )

    async def connect(self):
        rom.util.use_null_session()
        self.user = self.scope['user']
        await sync_to_async(self.user.refresh_from_db)()
        if not self.user:
            self.logger("Unauthorized action : Invalid user.", logger.error)
            return await self.close(1008, reason="Invalid user")
        if not self.user.is_authenticated:
            self.logger("Unauthorized action : User not authenticated", logger.error)
            return await self.close(1008, reason="User not authenticated")
        self.player = await sync_to_async(models.LobbyPlayer.get_by_user)(self.user)
        if not self.player or not self.player.lobby:
            self.logger("Unauthorized action : You are not in a lobby", logger.error)
            return self.close(1008, reason="You are not in a lobby")
        await self.add_to_group("player") 
        await self.add_to_group("lobby")
        self.player.ws_status = WebsocketStatus.CONNECTED
        await sync_to_async(self.player.save)()
        if self.user.status == Status.OFF:
            await sync_to_async(self.change_status)(Status.ON)
        await self.accept()

    async def remove_from_lobby(self):
        await sync_to_async(leave_lobby_api)(self.player, back_to_main_lobby=False)
        await sync_to_async(self.player.refresh)(force=True)

    def change_status(self, status):
        self.user.status = status
        self.user.save()
        notify_friends_api(self.user)

    async def disconnect(self, close_code):
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
                await sync_to_async(self.change_status)(Status.OFF)
        else:
            await sync_to_async(self.player.refresh)(force=True)
            if self.player.lobby:
                await self.remove_from_lobby()
            await sync_to_async(self.change_status)(Status.OFF)

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