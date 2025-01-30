import pyfiglet, colorama, time, curses, os, time
from profile import Profile
from colorama import Fore, Style
from .game import main
from .api_requests import API_requests

global COLOR
COLOR_TITLE = Fore.YELLOW
COLOR_AUTHORS = Fore.GREEN

class Menu:
    def __init__(self):
        self.api = API_requests()
        self.auth = 0
        self.color = Fore.CYAN
    
    def screentitle(self):
        os.system("clear")
        title = pyfiglet.figlet_format("Pong Game", font="doom") + "CLI Version"
        authors = "==== By Nily, Théo and Nassima ===="
        print(COLOR_TITLE + title + Style.RESET_ALL)
        time.sleep(0.2)
        print(COLOR_AUTHORS + authors)
        print(self.color)
        print("\033[s")

    def options_display(self):
        while True:
            if self.auth:
                cmd = input("\033[u\033[J" + self.color + "> Enter a command (PROFILE/PONG/FRIENDS/HISTORY/COLORS/LOGOUT/QUIT): ").lower()
                if cmd == 'profile':
                    self.display_profile()
                elif cmd == 'pong':
                    self.play()
                elif cmd == 'friends':
                    self.display_friends()
                elif cmd == 'history':
                    self.display_history()
                elif cmd == 'colors':
                    self.color_change()
                elif cmd == 'logout':
                    self.auth = 0
                elif cmd == 'quit':
                    print("Exiting the CLI...")
                    break
                else:
                    print("Invalid command")
            else:
                cmd = input("\033[u\033[J" + self.color + "> Enter a command (LOGIN/SIGNUP/QUIT): ").lower()
                if cmd == 'login':
                    self.auth = self.api.get_creditentials()
                elif cmd == 'signup':
                    self.api.get_sign_up_details()
                elif cmd == 'quit':
                    print("Exiting the CLI...")
                    break
                else:
                    print("Invalid command")

    def color_change(self):
        while True:
            color = input("\033[u\033[J" + self.color + "> Enter a color (CYAN/RED/GREEN/BLUE/MAGENTA/WHITE/MENU): ").lower()
            if color == 'cyan':
                self.color = Fore.CYAN
                print(self.color + "Color changed to " + color + " successfully")
                time.sleep(0.3)
            elif color == 'red':
                self.color = Fore.RED
                print(self.color + "> Color changed to " + color + " successfully")
                time.sleep(0.3)
            elif color == 'green':
                self.color = Fore.GREEN
                print(self.color + "> Color changed to " + color + " successfully")
                time.sleep(0.3)
            elif color == 'blue':
                self.color = Fore.BLUE
                print(self.color + "> Color changed to " + color + " successfully")
                time.sleep(0.3)
            elif color == 'magenta':
                self.color = Fore.MAGENTA
                print(self.color + "> Color changed to " + color + " successfully")
                time.sleep(0.3)
            elif color == 'white':
                self.color = Fore.WHITE
                print(self.color + "> Color changed to " + color + " successfully")
                time.sleep(0.3)
            elif color == 'menu':
                break
            else:
                print("Invalid command")
                time.sleep(0.3)

    def display_profile(self):
        os.system("clear")
        self.api.update_profile()
        self.api.update_stats()
        print(f"\033[H{self.api.user.avatar}")
        print(f"\033[1;41HPlayer: {self.api.user.username}")
        print(f"\033[2;41HRank: {self.api.user.rank}")
        print(f"\033[3;41HFriends: {len(self.api.user.friends)}")
        print(f"\033[5;41HGames played: {self.api.user.stats['total_games_played']}")
        print(f"\033[6;41HGames Won: {self.api.user.stats['games_won']}")
        print(f"\033[7;41HGames Lost: {self.api.user.stats['total_games_played'] - self.api.user.stats['games_won']}")
        cmd = input("\033[23;0H> Display statistics and performance metrics (YES/NO): ").lower()
        if cmd == "yes":
            print(f"\033[9;41HAverage Score: {self.api.user.stats['average_score']}")
            print(f"\033[10;41HWin Streak: {self.api.user.stats['win_streak']}")
            print(f"\033[11;41HWin Loss Ratio: {self.api.user.stats['win_loss_ratio']}")
            cmd = input("\033[23;0H\033[J> Back to the menu (MENU): ").lower()
        os.system("clear")
        self.screentitle()

    def play(self):
        if self.api.game_init():
            curses.wrapper(main)
            self.screentitle()

    def display_friends(self):
        while True:
            cmd = input("\033[u\033[J> Choose option (ADD/REMOVE/LIST/MENU):").lower()
            if cmd == "add":
                name = input("> Enter user name: ")
                if self.api.add_friend(name):
                    print("Friend added successfully.")
                else:
                    print("No user of this name found.")
                time.sleep(0.4)
            elif cmd == "remove":
                name = input("> Enter user name: ")
                if self.api.remove_friend(name):
                    print("Friend removed successfully.")
                else:
                    print("No friend of this name found.")
                time.sleep(0.4)
            elif cmd == "list":
                self.api.update_profile()
                page = 0
                size = 2
                online = 0
                #idx = 0
                while True:
                    print("\033[u\033[JFRIEND LIST: ")
                    """if online == 1:
                        for i in range(size):
                            if page * size + idx >= len(self.api.user.friends):
                                break
                            while not self.api.user.friends[page * size + idx]['status'] == {'online', 'in game'}:
                                idx +=1
                            if self.api.user.friends[page * size + idx]['status'] == {'online', 'in game'}:
                                print(f"{self.api.user.friends[page * size + idx]['username']} | {self.api.user.friends[page * size + idx]['status']}")"""

                    for i in range(size):
                        if page * size + i >= len(self.api.user.friends):
                            break
                        if online == 1 and self.api.user.friends[page * size + i]['status'] == {'online', 'in game'}:
                            print(f"{self.api.user.friends[page * size + i]['username']} | {self.api.user.friends[page * size + i]['status']}")
                        elif online == 0:
                            print(f"{self.api.user.friends[page * size + i]['username']} | {self.api.user.friends[page * size + i]['status']}")
                    cmd = input("> Choose option (PREV/NEXT/ONLINE/ALL/BACK): ").lower()
                    if cmd == "prev":
                        if page >= 1:
                            page -= 1
                    elif cmd == "next":
                        if page * size + size < len(self.api.user.friends):
                            page += 1
                    elif cmd == "online":
                        online = 1
                        page = 0
                        #idx = 0
                    elif cmd == "all":
                        online = 0
                        page = 0
                    elif cmd == "back":
                        break
                    else:
                        print("Invalid command.")
            elif cmd == "menu":
                break
            else:
                print("Invalid commad.")
        return
    
    def display_history(self):
        # display mode, dates, score, performance
        cmd = input("\033[u\033[J> Move page (PREV/NEXT/MENU): ").lower()
