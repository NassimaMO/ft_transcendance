import requests
import jwt
import time
import logging
from typing import Optional
from .api_connector import APIConnector

logger = logging.getLogger('default')


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
    """
    
    def __init__(self) -> None:
        """
        Initializes APIAuth with token and username attributes.
        
        Inherits APIConnector initialization to set up the base API URL.
        """
        super().__init__()
        self.access_token = None
        self.refresh_token = None
    
    def get_register_url(self) -> str:
        """
        Returns the API URL for user registration.
        """
        return self.base_url + 'users/me/'

    def get_login_url(self) -> str:
        """
        Returns the API URL for user login.
        """
        return self.base_url + 'tokens/'
    
    def get_refresh_url(self) -> str:
        """
        Returns the API URL for refreshing the access token.
        """
        return self.base_url + 'tokens/refresh/'
    
    def _refresh_token(self) -> requests.Response:
        """
        Sends a POST request to refresh the access token using the refresh token.
        
        If successful, updates the access token.
        """
        url = self.get_login_url()
        data = {'refresh': self.refresh_token}
        response = self.api_request(url, data, method="POST")
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
    
    def register(self, username: str, password: str, verbose: bool = False) -> requests.Response:
        """
        Registers a new user via the API.
        
        Sends a POST request with the provided username and password. You need to LOGIN then to get tokens.
        """
        url = self.get_register_url()
        data = {'username': username, 'password': password}
        response = self.api_request(url, data, method="POST")
        if response.status_code == 201:
            if verbose:
                print("Registration successful")
        elif response.status_code == 400 :
            if verbose:
                print("Registration did not complete because of invalid username or password given")
        else:
            if verbose:
                print(f"Erreur: {response.status_code}")
        return response
    
    def login(self, username: str, password: str, verbose: bool = False) -> requests.Response:
        """
        Logs in a user and retrieves JWT tokens.
        
        Sends a POST request with the provided username and password, then stores the access and refresh tokens.
        """
        url = self.get_login_url()
        data = {'username': username, 'password': password}
        response = self.api_request(url, data, method="POST")
        if response.status_code == 200:
            self.access_token = response.json().get('access')
            self.refresh_token = response.json().get('refresh')
            if verbose:
                print("Login successful")
        elif response.status_code == 400 :
            logger.error("Login failed because of invalid username or password given")
            if verbose:
                print("Login failed because of invalid username or password given")
        else:
            logger.error(f"Erreur: {response.status_code}")
            if verbose:
                print(f"Erreur: {response.status_code}")
        return response


if __name__ == "__main__":
    # Example usage of APIAuth:
    
    # Initialize the APIAuth class
    auth = APIAuth()

    # Register a new user
    response = auth.register("new_user", "password", verbose=True)

    # Log in an existing user
    response = auth.login("new_user", "password", verbose=True)

    # Optional : get the access token for authenticated requests
    token = auth.get_token()
    print("Token: ", token)