import getpass, time, requests
from cli_api.api_pong import APIPong
from cli_app.image_to_ascii import image_to_ascii

class User:

    def __init__(self):
        self.username = None
        self.avatar = None
        self.history = None
        self.rank = None
        self.stats = None
        self.friends = None

class API_requests(APIPong):

    def __init__(self):
        super().__init__()
        self.user = User()
        self.profile = None
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
            time.sleep(0.3)
            return 0
        self._log(username)
        time.sleep(0.3)
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

    def _log(self, username):
        self.user.username = username
        self.update_profile()
        self.update_stats()

    def get_profile_url(self):
        return self.get_base_url() + "profile/"
    
    def get_statistics_url(self):
        return self.get_base_url() + "stats/"
    
    def add_friend(self, name):
        return 1

    def remove_friend(self, name):
        return 1
    
    def update_profile(self):
        self.profile = self.get_response_GET(self.get_profile_url())
        image_response = requests.get(self.profile['avatar']['avatar_url'])
        if image_response.status_code == 200:
            with open('avatar.png', 'wb') as file:
                file.write(image_response.content)
            self.user.avatar = image_to_ascii('avatar.png')
        self.user.rank = "Ranked beyond comprehension." #requests.get(self.profile['rank']['rank'])
        self.user.history = "" #requests.get(self.profile['history'])
        self.user.friends = [{'username': 'Nily', 'status': 'online'}, {'username': 'Theo', 'status': 'in game'}, {'username': 'Bot1', 'status': 'online'}] #, {'username': 'Bot2', 'status': 'offline'}] #requests.get(self.profile['friends'])

    def update_stats(self):
        self.user.stats = self.get_response_GET(self.get_statistics_url())

    
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
            return 1 # get game logic