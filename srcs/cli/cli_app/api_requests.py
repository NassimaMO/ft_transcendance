import getpass, time
from cli_api.api_pong import APIPong

class User_info:

    def __init__(self):
        self.username = None
        self.history = None
        self.profile = None

class API_requests(APIPong):

    def __init__(self):
        super().__init__()
        self.user = User_info()
        self.websocket = None
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
        response = super().login(username, password) #auth
        if int(response.status_code / 100) != 2:
            print("> Wrong login creditentials.")
            time.sleep(0.4)
            return 0
        self.log(username)
        time.sleep(0.4)
        return 1
    
    def get_sign_up_details(self):
        username = input("> Enter your username: ")
        while True:
            password = getpass.getpass("> Enter your password: ")
            re_password = getpass.getpass("> Confirm your password: ")
            if username and password and password == re_password:
                break
            print("> The passwords entered are different. Try again.")
        if super().register(username, password)[:1] == 2: #auth
            print("Player registered successfully.")
            return
        print("") #response error

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
        # display avatar, name, rank, number of matches, number of wins, friends
        cmd = input("> Display more statistics (YES/NO/MENU): ").lower()
        return
    
    def display_friends(self):
        cmd = input("> Choose option: (ADD/REMOVE/LIST/MENU)").lower()
        return

    def update_history(self):
        return
    
    def display_history(self):
        # display mode, dates, score, performance
        cmd = input("> Move page (PREV/NEXT/MENU): ").lower()
        return

    def game_init(self):
        mode = None
        mm_preferences = None
        while True:
            connexion = input("> Choose game connexion (LOCAL/ONLINE/BACK): ").lower()
            
            if connexion == "local":
                
                while True:
                    mode = input("> Choose game mode (SOLO/1V1/BACK): ").lower()
                    if mode == "solo" or mode == "1v1" or mode == "back":
                        mm_preferences = "unranked"
                        break
                    else:
                        print("Invalid command.")
            
            
            elif connexion == "online":
                while True:
                    mode = input("> Choose game mode (SOLO/1V1/2V2/BACK): ").lower()
                    if mode == "solo" or mode == "1v1" or mode == "2v2":
                        while True:
                            mm_preferences = input("> Choose matchmaking preference (RANKED/UNRANKED/TOURNAMENT/BACK):")
                            if mm_preferences == "ranked" or mm_preferences == "unranked" or mm_preferences == "tournament" or mm_preferences == "back":
                                break
                            else:
                                print("Invalid command.")
                        if mm_preferences != "back":
                            break
                    elif mode == "back":
                        break
                    else:
                        print("Invalid command.")


            else:
                print("Invalid command.")
            
            if connexion == "back":
                return 0
            elif mode and (mode != "back" and mm_preferences != "back"):
                break
        
        
        response = super().select_mode(connexion, mode, mm_preferences) #play
        if int(response.status_code / 100) == 2:
            return 1 # get game logic