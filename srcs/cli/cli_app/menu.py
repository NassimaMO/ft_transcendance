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
            print("\033[u\033[J") # the color does not change
            if AUTH:
                cmd = input("> Enter a command (PROFILE/PONG/HISTORY/COLORS/LOGOUT/QUIT): ")
                if cmd == 'PROFILE':
                    self.api.display_profile()
                elif cmd == 'PONG':
                    curses.wrapper(main)
                    self.api.update_history()
                elif cmd == 'HISTORY':
                    self.api.display_history()
                elif cmd == 'COLORS':
                    self.color_change()
                elif cmd == 'LOGOUT':
                    AUTH = self.api.logout()
                elif cmd == 'QUIT':
                    print("Exiting the CLI...")
                    break
                else:
                    print("Invalid command")
            else:
                cmd = input("> Enter a command (LOGIN/SIGNUP/QUIT): ")
                if cmd == 'LOGIN':
                    AUTH = self.api.get_creditentials()
                elif cmd == 'SIGNUP':
                    self.api.get_sign_up_details()
                elif cmd == 'QUIT':
                    print("Exiting the CLI...")
                    break
                else:
                    print("Invalid command")

    def color_change(self):
        while True:
            color = input("> Enter a color (CYAN/RED/GREEN/BLUE/MAGENTA/WHITE/MENU): ")
            if color == 'CYAN':
                COLOR = Fore.CYAN
                print(COLOR + "Color changed to " + color + " successfully")
            elif color == 'RED':
                COLOR = Fore.RED
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'GREEN':
                COLOR = Fore.GREEN
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'BLUE':
                COLOR = Fore.BLUE
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'MAGENTA':
                COLOR = Fore.MAGENTA
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'WHITE':
                COLOR = Fore.WHITE
                print(COLOR + "> Color changed to " + color + " successfully")
            elif color == 'MENU':
                break
            else:
                    print("Invalid command")
