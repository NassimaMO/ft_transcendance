import os

class APIConnector:
    """
    This class is responsible for managing the base URL for API connections.
    
    Attributes:
        base_url (str): The base URL of the API, built dynamically depending on the environment.
    """
    
    def __init__(self, base_url: str = 'default') -> None :
        """
        Initializes the APIConnector by setting the base URL.
        If no base URL is provided, the default base URL is constructed based on the environment context.
        
        Args:
            base_url (str): The base URL for the API. Defaults to 'default', which is replaced by an auto-configured URL.
        """
        if base_url == 'default':
            context = os.environ.get("CONTEXT")
            if context == "dev":
                protocol = 'http'
                port = ':8000'
            else:
                protocol = 'https'
                port = ''
            base_url = f"{protocol}://host.docker.internal{port}/"
        if base_url[-1] != '/':
            base_url += '/'
        self.base_url = base_url

    def get_base_url(self) -> str:
        """
        Returns the base URL of the API.
        
        Returns:
            str: The base URL of the API.
        """
        return self.base_url