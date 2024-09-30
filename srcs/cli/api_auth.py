import requests
import urllib3
from typing import Optional
from api_connector import APIConnector

class APIAuth(APIConnector):
    """
    This class handles authentication operations such as registering a new user and logging in.
    It inherits from APIConnector to make use of the base_url.
    
    Attributes:
        token (Optional[str]): The authentication token obtained after login or registration.
    """
    
    def __init__(self, base_url: str = 'default') -> None :
        """
        Initializes the APIAuth class by calling the APIConnector's initializer
        and setting the token to None initially.
        
        Args:
            base_url (str): The base URL for the API. Defaults to 'default'.
        """
        super().__init__(base_url)
        self.token = None
    
    def get_register_url(self) -> str:
        """
        Constructs and returns the URL for user registration.
        
        Returns:
            str: The URL for the registration endpoint.
        """
        return self.base_url + 'api/users/'

    def get_login_url(self) -> str:
        """
        Constructs and returns the URL for user login.
        
        Returns:
            str: The URL for the login endpoint.
        """
        return self.base_url + 'api/users/login/'
    
    def register_user(self, username: str, password: str) -> requests.Response:
        """
        Registers a new user by making a POST request to the registration endpoint.

        Args:
            username (str): The desired username for the new user.
            password (str): The password for the new user.

        Returns:
            requests.Response: The full HTTP response from the registration request, containing status, data, etc.
        """
        url = self.get_register_url()
        data = {
            'username': username,
            'password': password,
        }
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(url, json=data, verify=False)
        
        if response.status_code == 201:
            print("User created successfully.")
            self.token = response.json().get('token')
        else:
            print(f"Failed to create user. Error: {response.status_code}")
        return response
    
    def login_user(self, username: str, password: str) -> requests.Response:
        """
        Logs in an existing user by making a POST request to the login endpoint.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            requests.Response: The full HTTP response from the login request, containing status, token, etc.
        """
        url = self.get_login_url()
        data = {
            'username': username,
            'password': password,
        }
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(url, json=data, verify=False)
        
        if response.status_code == 200:
            print("Login successful.")
            self.token = response.json().get('token')
        else:
            print(f"Failed to login. Error: {response.status_code}")
        return response

    def get_token(self) -> Optional[str]:
        """
        Returns the currently stored authentication token.

        Returns:
            Optional[str]: The authentication token if it exists, None otherwise.
        """
        return self.token


if __name__ == "__main__" :
    # Example usage:

    # Initialize the APIAuth with the default base URL (determined by the environment context)
    auth = APIAuth() # or auth = APIAuth("https://some_url") with a specified url

    # Register a new user
    auth.register_user("testuser", "password123")

    # Use the token for all further requests
    print(f"Token: {auth.get_token()}")

    # Log in an existing user
    auth.login_user("testuser", "password123")
    print(f"Login Token: {auth.get_token()}")
