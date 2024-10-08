import requests
import jwt
import time
from typing import Optional
from api_connector import APIConnector


class APIAuth(APIConnector):
    """
    APIAuth class manages user authentication and JWT token handling via the API.
    
    Inherits from APIConnector to utilize API connection features, adding methods for user registration, login, and JWT token management 
    (including automatic refresh).

    Attributes:
    ----------
    access_token : str | None
        JWT access token for authenticating requests. Automatically refreshed if expired.
    
    refresh_token : str | None
        JWT refresh token used to request a new access token when expired.

    username : str | None
        Username used during registration or login.

    Methods:
    --------
    get_register_url() -> str :
        Returns the API URL for user registration.
    
    get_login_url() -> str :
        Returns the API URL for user login and JWT retrieval.
    
    get_refresh_url() -> str :
        Returns the API URL for refreshing the access token.

    _refresh_token() -> requests.Response :
        Sends a request to refresh the access token using the current refresh token.

    _check_token() -> None :
        Checks if the access token is expired and refreshes it if necessary.

    get_token() -> Optional[str] :
        Returns the current access token, refreshing it if needed.

    get_headers() -> dict :
        Returns HTTP headers, including the Authorization header with the access token if available.

    register(username: str, password: str) -> requests.Response :
        Registers a new user with the provided username and password.

    login(username: str, password: str) -> requests.Response :
        Logs in a user and retrieves the JWT access and refresh tokens.
    """
    
    def __init__(self) -> None:
        """
        Initializes APIAuth with token and username attributes.
        
        Inherits APIConnector initialization to set up the base API URL.
        """
        super().__init__()
        self.access_token = None
        self.refresh_token = None
        self.username = None
    
    def get_register_url(self) -> str:
        """
        Returns the API URL for user registration.
        """
        return self.base_url + 'register/'

    def get_login_url(self) -> str:
        """
        Returns the API URL for user login.
        """
        return self.base_url + 'token/'
    
    def get_refresh_url(self) -> str:
        """
        Returns the API URL for refreshing the access token.
        """
        return self.base_url + 'token/refresh/'
    
    def _refresh_token(self) -> requests.Response:
        """
        Sends a POST request to refresh the access token using the refresh token.
        
        If successful, updates the access token.
        """
        url = self.get_login_url()
        data = {'refresh': self.refresh_token}
        response = self.get_response(url, data)
        if response.status_code == 200:
            self.access_token = response.json().get('access')
        return response
    
    def _check_token(self) -> None:
        """
        Checks if the access token is expired and refreshes it if necessary.
        """
        if self.access_token :
            decoded_token = jwt.decode(self.access_token, options={"verify_signature": False})
            if decoded_token['exp'] < time.time():
                self._refresh_token()

    def get_token(self) -> Optional[str]:
        """
        Returns the access token after checking and refreshing it if needed.
        """
        self._check_token()
        return self.access_token
    
    def get_headers(self) -> dict:
        """
        Returns HTTP headers including the JWT access token if available.
        """
        if self.get_token():
            return {'Authorization': f'Bearer {self.get_token()}', **super().get_headers()}
        return super().get_headers()
    
    def register(self, username: str, password: str) -> requests.Response:
        """
        Registers a new user via the API.
        
        Sends a POST request with the provided username and password. You need to LOGIN then to get tokens.
        """
        url = self.get_register_url()
        data = {'username': username, 'password': password}
        response = self.get_response(url, data)
        if response.status_code == 201:
            self.username = response.json().get("username")
            print("Registration successful")
        elif response.status_code == 400 :
            print("Registration did not complete because of invalid username or password given")
        return response
    
    def login(self, username: str, password: str) -> requests.Response:
        """
        Logs in a user and retrieves JWT tokens.
        
        Sends a POST request with the provided username and password, then stores the access and refresh tokens.
        """
        url = self.get_login_url()
        data = {'username': username, 'password': password}
        response = self.get_response(url, data)
        if response.status_code == 200:
            self.access_token = response.json().get('access')
            self.refresh_token = response.json().get('refresh')
            print("Login successful")
        return response


if __name__ == "__main__":
    # Example usage of APIAuth:
    
    # Initialize the APIAuth class
    auth = APIAuth()

    # Register a new user
    response = auth.register("user", "password")

    # Optional : get the access token for authenticated requests
    token = auth.get_token()

    # Log in an existing user
    response = auth.login("user", "password")
