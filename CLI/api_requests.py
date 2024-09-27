import requests, getpass

API_url = 'https://localhost'

class User_info:

    def __init__(self):
        self.username = ""
        self.history = ""
        self.profile = ""
        self.pos = 0

class API_requests:

    def __init__(self):
        self.key = ""
        self.user = User_info()
        return
    
    def get_creditentials(self):
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")
        return username, password
    
    def get_sign_up_details(self):
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")
        re_password = getpass.getpass("Confirm your password: ")
        return username, password
    
    def authentication(self, username, password):
        return token

    def fetch_game_logic(self):
        return ball, paddle, score