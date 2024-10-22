import pyfiglet, colorama, time, curses, os, time
from game import main
from cli_app.api_requests import API_requests
from colorama import Fore, Style

AUTH = 0
COLOR = Fore.CYAN
COLOR_TITLE = Fore.YELLOW
COLOR_AUTHORS = Fore.GREEN

class Menu:
    def __init__(self):
        self.api = API_requests()
        return 
    
    def screentitle(self):
        os.system("clear")
        title = pyfiglet.figlet_format("Pong Game", font="doom") + "CLI Version"
        authors = "==== By Nily, Théo and Nassima ===="
        print(COLOR_TITLE + title + Style.RESET_ALL)
        time.sleep(0.2)
        print(COLOR_AUTHORS + authors)
        print(COLOR)
        print("\033[s")

    def options_display(self):
        global AUTH
        while True:
            if AUTH:
                cmd = input("\033[u\033[J> Enter a command (PROFILE/PONG/FRIENDS/HISTORY/COLORS/LOGOUT/QUIT): ").lower()
                if cmd == 'profile':
                    self.display_profile()
                elif cmd == 'pong':
                    if self.api.game_init():
                        curses.wrapper(main)
                        self.api.update_history()
                elif cmd == 'friends':
                    self.display_friends()
                elif cmd == 'history':
                    self.display_history()
                elif cmd == 'colors':
                    self.color_change()
                elif cmd == 'logout':
                    AUTH = 0
                elif cmd == 'quit':
                    print("Exiting the CLI...")
                    break
                else:
                    print("Invalid command")
            else:
                cmd = input("\033[u\033[J> Enter a command (LOGIN/SIGNUP/QUIT): ").lower()
                if cmd == 'login':
                    AUTH = self.api.get_creditentials()
                elif cmd == 'signup':
                    self.api.get_sign_up_details()
                elif cmd == 'quit':
                    print("Exiting the CLI...")
                    break
                else:
                    print("Invalid command")

    def color_change(self):
        while True:
            color = input("\033[u\033[J> Enter a color (CYAN/RED/GREEN/BLUE/MAGENTA/WHITE/MENU): ").lower()
            if color == 'cyan':
                COLOR = Fore.CYAN
                print(COLOR + "Color changed to " + color + " successfully")
            elif color == 'red':
                COLOR = Fore.RED
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'green':
                COLOR = Fore.GREEN
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'blue':
                COLOR = Fore.BLUE
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'magenta':
                COLOR = Fore.MAGENTA
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'white':
                COLOR = Fore.WHITE
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'menu':
                break
            else:
                    print("Invalid command")

    def display_profile(self):
        os.system("clear")
        #print("\033[u\033[J")
        for i in range(25):
            print("*" * 50) # + self.api.get_avatar(), end='')
        print(f"\033[H\033[50C" + "Player: " + self.api.get_username())
        print("\033[50C" + "Description: " + self.api.get_description())
        print("\033[50C" + "Rank: " + self.api.get_rank())
        print("\033[50C" + "Friends: " + self.api.get_friends())
        print("\033[50C" + "Stats: " + self.api.get_stats())
        cmd = input("\033[26H> Display more statistics (YES/NO): ").lower()
        if cmd == "yes":
            print("\033[H\033[50C" + "Detailed stats: " + self.api.get_stats())
            cmd = input("\033[26H\033[J> Back to the menu (MENU): ").lower()
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
                while True:
                    print("\033[u\033[JFRIEND LIST: ")
                    cmd = input("> Choose option (PREV/NEXT/ONLINE/ALL/BACK): ").lower()
                    if cmd == "prev":
                        print("")
                    elif cmd == "next":
                        print("")
                    elif cmd == "online":
                        print("")
                    elif cmd == "all":
                        print("")
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
        return