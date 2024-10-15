import getpass
from cli_api.api_auth import APIAuth

class User_info:

    def __init__(self):
        self.username = None
        self.history = None
        self.profile = None

class API_requests(APIAuth):

    def __init__(self):
        super().__init__()
        self.user = User_info()
        return
    
    def get_creditentials(self):
        while True:
            username = input("> Enter your username: ")
            if username:
                break
            print("> Please enter a username.")
        while True:
            password = getpass.getpass("> Enter your password: ")
            if password:
                break
            print("> Please enter a password.")
        response = super().login(username, password)
        if response == 200:
            self.log(username)
        elif response == 401:
            print("> Wrong login creditentials.")
            return 0
        return 1
    
    def get_sign_up_details(self):
        username = input("> Enter your username: ")
        while True:
            password = getpass.getpass("> Enter your password: ")
            re_password = getpass.getpass("> Confirm your password: ")
            if username and password and password == re_password:
                break
            print("> The passwords entered are different. Try again.")
        return super().register(username, password)

    def log(self, username):
        self.username = username
        #self.token = super().get_token()
        self.profile = self.get_profile()
        self.history = self.update_history()

    def logout(self):
        #self.user.username, self.user.profile, self.user.history = None
        return 0

    def get_profile(self):
        return
    
    def display_profile(self):
        return

    def update_history(self):
        return
    
    def display_history(self):
        return

    def fetch_game_logic(self):
        ball, paddle, score = 1
        return ball, paddle, score