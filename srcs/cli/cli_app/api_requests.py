import getpass, time
from cli_api.api_pong import APIPong
from cli_app.image_to_ascii import image_to_ascii

class User_info:

    def __init__(self):
        self.username = None
        self.avatar = None
        self.description = None
        self.history = None
        self.rank = None
        self.stats = None
        self.friends = None

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
        if int(super().login(username, password).status_code / 100) != 2: #auth
            print("> Wrong login creditentials.")
            time.sleep(0.4)
            return 0
        self._log(username)
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
        if int(super().register(username, password).status_code / 100) == 2: #auth
            print("Player registered successfully.")
            return
        print("") #response error

    def _log(self, username):
        self.user.username = username
        self.user.avatar = image_to_ascii("/app/srcs/cli/cli_app/sheil.png")
        self.user.description = ""
        self.user.rank = ""
        self.user.history = self.update_history()
        self.user.stats = ""
        self.user.friends = ""

    def get_username(self):
        return self.user.username

    def get_avatar(self):
        return self.user.avatar
    
    def get_description(self):
        return self.user.description
    
    def get_history(self):
        return self.user.history
    
    def get_rank(self):
        return self.user.rank
    
    def get_stats(self):
        return self.user.stats
    
    def get_friends(self):
        return self.user.friends

    def update_history(self):
        return

    def game_init(self):
        mode = None
        mm_preferences = None
        while True:
            connexion = input("> Choose game connexion (LOCAL/ONLINE/BACK): ").lower()
            
            if connexion == "local":
                
                while True:
                    mode = input("> Choose game mode (SOLO/1V1/BACK): ").lower()
                    if mode in ("solo", "1v1", "back"):
                        mm_preferences = "unranked"
                        break
                    else:
                        print("Invalid command.")
            
            
            elif connexion == "online":
                while True:
                    mode = input("> Choose game mode (SOLO/1V1/2V2/BACK): ").lower()
                    if mode in ("solo", "1v1", "2v2"):
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
            elif mode and {mode, mm_preferences} != {"back"}:
                break
        
        
        response = super().select_mode(connexion, mode, mm_preferences) #play
        if int(response.status_code / 100) == 2:
            time.sleep(1)
            return 1 # get game logic