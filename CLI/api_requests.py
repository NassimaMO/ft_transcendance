import getpass

API_url = 'https://localhost'

class User_info:

    def __init__(self):
        self.username = None
        self.history = None
        self.profile = None
        self.token = None

class API_requests:

    def __init__(self):
        self.key = ""
        self.user = User_info()
        return
    
    def get_creditentials(self):
        username = input("Enter your username: ")
        while True:
            password = getpass.getpass("Enter your password: ")
            if password:
                break
            print("> Please enter a VALID password ???????")
        return username, password
    
    def get_sign_up_details(self):
        username = input("Enter your username: ")
        while True:
            password = getpass.getpass("Enter your password: ") # Need to validate username
            re_password = getpass.getpass("Confirm your password: ")
            if username and password and password == re_password: # Maybe also check if the password is valid (ex: > 8 length)
                break
            command = input("The passwords entered are different. Try again or go back to the main menu. (RETRY/MENU): ")
            if command == 'MENU':
                return
        return username, password
    
    def authentication(self, username, password):
        self.token = 0
        if username and password:
            #websocket thingy
            self.log(username)
            self.token = 1
        else:
            print("> Back to the menu we go...")
        return self.token

    def log(self, username):
        self.username = username
        self.profile = self.get_profile()
        self.history = self.update_history()

    def delog(self):
        self.username, self.profile, self.history = None
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