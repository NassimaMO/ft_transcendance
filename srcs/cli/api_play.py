from api_auth import APIAuth
import asyncio
import websockets
import json
import requests


class APIPlay(APIAuth):
    """
    APIPlay class extends APIAuth to manage game-related API calls and matchmaking over WebSockets.
    
    This class handles selecting game modes, initiating matchmaking, and receiving real-time updates about match status.
    
    Attributes:
    -----------
    match_choice_id : str or None
        Stores the ID of the selected game mode, required for matchmaking.
    
    need_matchmaking : bool
        Indicates whether matchmaking is required based on the selected mode.
    
    websocket : WebSocketClientProtocol or None
        Represents the WebSocket connection used for matchmaking.

    Methods:
    --------
    get_play_url() -> str :
        Constructs the URL for initiating a game request.
    
    get_match_url() -> str :
        Constructs the WebSocket URL for matchmaking based on the chosen game mode.
    
    select_mode(connect_choice: str, mode_choice: str, mm_choice: str) -> requests.Response :
        Sends a POST request to the server to select a game mode and sets matchmaking parameters.
    
    matchmaking() -> None :
        Opens a WebSocket connection and listens for matchmaking updates. Continues to receive messages until a match is found.
    
    play(connect_choice: str = None, mode_choice: str = None, mm_choice: str = None) -> None :
        Combines the game mode selection and matchmaking process, running asynchronously to avoid blocking.
    """
    
    def __init__(self) -> None:
        """
        Initializes the APIPlay class by inheriting from APIAuth.
        
        Initializes match_choice_id to None and prepares the object for game mode selection and matchmaking.
        """
        super().__init__()
        self.match_choice_id = None

    def get_play_url(self) -> str:
        """
        Returns the full URL to start the game play request.
        
        This URL is used to post the game mode selection and matchmaking preferences to the server.
        """
        return self.get_base_url() + "play/"
    
    def get_match_ws_url(self) -> str:
        """
        Returns the WebSocket URL for matchmaking based on the selected game mode (match_choice_id).
        
        Returns an empty string if match_choice_id is not set.
        """
        return self.get_base_url('ws') + "matchmaking/" + f"{self.match_choice_id}" if self.match_choice_id else ""

    def select_mode(self, connect_choice: str, mode_choice: str, mm_choice: str) -> requests.Response:
        """
        Selects the game mode by sending a POST request with connection type, game mode, and matchmaking preference.
        
        Updates the match_choice_id and need_matchmaking attributes based on the server response.
        
        Parameters:
        -----------
        connect_choice : str
            The type of connection (e.g., "online").
        
        mode_choice : str
            The chosen game mode (e.g., "multi").
        
        mm_choice : str
            The matchmaking preference (e.g., "unranked").
        
        Returns:
        --------
        requests.Response :
            The HTTP response from the server indicating whether the game mode selection was successful or failed.
        """
        url = self.get_play_url()
        data = {
            'connect': connect_choice,
            'mode': mode_choice,
            'mm': mm_choice
        }
        response = self.get_response(url, data)
        if response.status_code == 201:
            self.match_choice_id = response.json().get("match_choice_id")
            self.need_matchmaking = response.json().get("matchmaking")
            print('Mode de jeu selectionné avec succès.')
        elif response.status_code == 400:
            print("Erreur de paramètres. Veuillez consulter la documentation de l'API.", response)
        elif response.status_code == 401:
            print(f"Erreur d'authentification : vous devez être correctement authentifié avant de lancer cette requête.")
        else:
            print(f"Erreur : {response.status_code} - {response}")
        return response
    
    async def matchmaking(self) -> None:
        """
        Initiates matchmaking by connecting to the WebSocket server and listens for matchmaking messages.
        
        The WebSocket connection remains open until a match is found or the connection is closed.
        """
        self.websocket = await self.connect_ws(self.get_match_ws_url())
        if self.websocket:
            print("Matchmaking started")
            try:
                while True:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    
                    if data.get("type") == "match_found":
                        print("Match found!")
                        self.match_url = data.get("match_url")
                        break
                    
                    elif "message" in data:
                        print(data["message"])
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Disconnected from matchmaking: {e}")
    
    def play(self, connect_choice: str = None, mode_choice: str = None, mm_choice: str = None) -> None:
        """
        Initiates the game play process by selecting a mode and running matchmaking if required.
        
        This method first ensures a game mode is selected, and then starts matchmaking asynchronously if needed.
        """
        if not connect_choice or not mode_choice or not mm_choice:
            if not self.match_choice_id:
                print("Veuillez choisir un mode de jeu")
                return
        else:
            self.select_mode(connect_choice, mode_choice, mm_choice)
        if not self.match_choice_id:
            print("Veuillez choisir un mode de jeu")
            return
        if self.need_matchmaking:
            asyncio.run(self.matchmaking())

if __name__ == "__main__" :
    api_play = APIPlay()
    api_play.register("user1", "password")
    api_play.login("user1", "password")
    api_play.select_mode("online", "multi", "unranked")
    api_play.play()
