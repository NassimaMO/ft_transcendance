import asyncio
import websockets
import json
import requests
from .api_auth import APIAuth


class APIPlay(APIAuth):
    
    def __init__(self) -> None:
        super().__init__()
        self.mm_websocket = None
        self.need_matchmaking = None
        self.lobby = None

    def get_lobby_url(self, main=True, id=None) -> str:
        if main:
            url = "users/me/lobbies/main/"
        elif id :
            url = f"users/me/lobbies/{id}/"
        else:
            return None
        return self.get_base_url() + url

    def get_match_ws_url(self) -> str:
        return self.get_base_url('ws') + "matchmaking"
    
    def update_lobby(self, main=True, id=None, verbose=False):
        response = self.api_request(self.get_lobby_url(main, id), method="GET")
        if response.ok :
            self.lobby = response.json()
            if verbose:
                print("Lobby updated")
                # print(self.lobby)
        return response

    def join_lobby(self, main=True, id=None, verbose=False):
        response = self.api_request(self.get_lobby_url(main, id), method="POST")
        if response.status_code == 201 :
            if verbose:
                print("New lobby created")
        elif response.status_code == 200 :
            if verbose:
                print("Lobby already exists")
            if self.lobby:
                return self.lobby
        return self.update_lobby(main, id, verbose)

    def select_mode(self, connect_choice: str, mode_choice: str, mm_choice: str, verbose=False) -> requests.Response:
        data = {
            'match-choice': {
                'connectivity': connect_choice,
                'mode': mode_choice,
                'matchmaking': mm_choice
            }
        }
        response = self.api_request(self.get_lobby_url(), data, method="PATCH")
        if response.status_code == 200 or response.status_code == 201:
            self.need_matchmaking = response.json().get("need_matchmaking")
            if verbose:
                print('Mode de jeu selectionné avec succès.')
            self.update_lobby(verbose=True)
        elif response.status_code == 400 :
            if verbose :
                print(f"Erreur de paramètres : {response.json().get('errors')}")
                print("Veuillez consulter la documentation de l'API.")
        elif response.status_code == 401:
            if verbose:
                print(f"Erreur d'authentification : vous devez être correctement authentifié avant de lancer cette requête.")
        else:
            if verbose:
                print(f"Erreur : {response.status_code} - {response}")
        return response
    
    def start_matchmaking(self, verbose=False):
        data = {'status': "start"}
        response = self.api_request(self.get_lobby_url(), data, method="PUT")
        if response.status_code == 200 or response.status_code == 201:
            if verbose:
                print('Matchmaking successfully started.')
            self.update_lobby(verbose=True)
        elif response.status_code == 400 :
            if verbose :
                print(f"Erreur de paramètres : {response.json().get('errors')}")
                print("Veuillez consulter la documentation de l'API.")
        elif response.status_code == 401:
            if verbose:
                print(f"Erreur d'authentification : vous devez être correctement authentifié avant de lancer cette requête.")
        else:
            if verbose:
                print(f"Erreur : {response.status_code} - {response}")
        return response
    
    async def matchmaking(self, verbose=False) -> None:
        if not self.mm_websocket :
            self.mm_websocket = await self.connect_ws(self.get_match_ws_url())
        if self.mm_websocket:
            self.start_matchmaking(verbose)
            try:
                while True:
                    message = await self.mm_websocket.recv()
                    data = json.loads(message)
                    if data.get("type") == "match_found":
                        if verbose:
                            print("Match found!")
                        self.match_url = data.get("match_url")
                        break
                    elif "message" in data :
                        if verbose:
                            print(data["message"])
            except websockets.exceptions.ConnectionClosed as e:
                if verbose:
                    print(f"Disconnected from matchmaking: {e}")

    def play(self, verbose=False) -> None:
        if self.need_matchmaking:
            asyncio.run(self.matchmaking(verbose))

if __name__ == "__main__" :
    api_play = APIPlay()
    print('register')
    api_play.register("user2", "password", verbose=True)
    print('login')
    api_play.login("user2", "password", verbose=True)
    print('join_lobby')
    api_play.join_lobby(verbose=True)
    print('select_mode')
    api_play.select_mode("En ligne", "1v1", "Non Classé", verbose=True)
    print('play')
    api_play.play(verbose=True)
