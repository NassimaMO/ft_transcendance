import os
import websockets
import urllib3
import requests


class APIConnector:
    """
    APIConnector class facilitates connections to the Django application and API.
    
    This class is designed to manage HTTP and WebSocket connections, based on the environment context (development or production).
    
    Attributes:
    -----------
    ip : str
        The IP address of the server. 'host.docker.internal' is used to connect to Docker host.
    
    is_secured : bool
        Determines whether the connection is secured (HTTPS/WSS) or not (HTTP/WS), depending on the context.
    
    port : str
        The port number for the API. Defaults to 8000 in development, empty string for production.
    
    base_url : str
        The base URL for the API, dynamically generated based on the connection type and context (HTTP or HTTPS).
    
    Methods:
    --------
    get_base_url(protocol: str = 'http') -> str :
        Returns the base URL for HTTP or WebSocket connections based on the protocol.
    
    get_headers() -> dict :
        Returns the headers for API requests, defaulting to JSON content type.
    
    get_response(url: str, data: dict) -> requests.Response :
        Sends a POST request to the provided URL with JSON data and headers.
    
    connect_ws(uri: str) -> websockets.WebSocketClientProtocol :
        Establishes a WebSocket connection to the given URI, using headers for authentication.
    """

    def __init__(self) -> None:
        """
        Initializes the APIConnector class.
        
        Sets the server IP, connection security (HTTP/HTTPS), and port based on the context (development or production).
        The context is determined by an environment variable.
        """
        context = os.environ.get("CONTEXT")
        self.ip = 'host.docker.internal'
        if context == "dev":
            self.is_secured = False
            self.port = ':8000'
        else:
            self.is_secured = True
            self.port = ''
        self.base_url = f"http{'s' if self.is_secured else ''}://{self.ip}{self.port}/api/"

    def get_base_url(self, protocol: str = 'http') -> str:
        """
        Returns the base URL based on the protocol (HTTP or WebSocket).
        
        If the protocol is 'http', it returns the HTTP/HTTPS base URL.
        If the protocol is 'ws', it returns the WebSocket base URL.
        """
        if protocol.lower() == "http":
            return self.base_url
        return f"ws{'s' if self.is_secured else ''}://{self.ip}{self.port}/ws/"

    def get_headers(self) -> dict:
        """
        Returns the default headers for API requests, specifying JSON as the content type.
        """
        return {"Content-Type": "application/json"}
    
    def get_response(self, url: str, data: dict) -> requests.Response:
        """
        Sends a POST request to the specified URL with the provided data.
        
        Uses the JSON content type in headers and disables SSL verification warnings.
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.post(url, json=data, headers=self.get_headers(), verify=False)
    
    async def connect_ws(self, uri: str):
        """
        Establishes a WebSocket connection to the specified URI.
        
        Includes headers for authentication if needed. Handles various exceptions such as invalid URL or connection rejection.
        
        Returns:
        --------
        WebSocketClientProtocol or None: Returns the WebSocket object if the connection succeeds, or None on failure.
        """
        try:
            websocket = await websockets.connect(uri, extra_headers=self.get_headers())
            print("Connexion acceptée")
            return websocket
        except websockets.InvalidURI:
            print("Erreur : URL WebSocket invalide")
        except websockets.InvalidHandshake:
            print("Erreur : La connexion WebSocket a été rejetée")
        except Exception as e:
            print(f"Erreur : {e}")
