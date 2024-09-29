import pyfiglet, colorama, time, curses, os, time, getpass
from game import main
#from api_requests import API_requests
from colorama import Fore, Style

AUTH = 0
COLOR = Fore.CYAN
COLOR_TITLE = Fore.YELLOW
COLOR_AUTHORS = Fore.GREEN

class Menu:
    def __init__(self):
        #self.api = API_requests()
        return 
    
    def screentitle(self):
        os.system("clear")
        #terminal_width, terminal_height = self.get_terminal_size()
        title = pyfiglet.figlet_format("Pong Game", font="doom") + "CLI Version"
        authors = "==== By Nily, Théo and Nassima ===="
        print(COLOR_TITLE + title + Style.RESET_ALL)
        time.sleep(0.2)
        print(COLOR_AUTHORS + authors)
        print(COLOR)

    def options_display(self):
        global AUTH
        while True:
            if AUTH:
                cmd = input("> Enter command (profile/pong/history/colors/log out/quit): ")
                if cmd == 'profile':
                    self.show_profile()
                elif cmd == 'pong':
                    curses.wrapper(main)
                elif cmd == 'history':
                    print("pong")
                elif cmd == 'colors':
                    self.color_change()
                elif cmd == 'log out':
                    #self.authentication()
                    AUTH = 0
                elif cmd == 'quit':
                    print("> Hope you had some nice little games. Sayounara !")
                    break
                else:
                    print("> Invalid command")
            else:
                cmd = input("> Enter command (login/sign up/quit): ")
                if cmd == 'login':
                    #self.api.authentication(self.api.get_creditentials())
                    AUTH = 1
                elif cmd == 'sign up':
                    #self.authentication()
                    AUTH = 1
                elif cmd == 'quit':
                    print("> Didn't even bother to log in.. Ha ! Good riddance !")
                    break
                else:
                    print("> Invalid command")

    def color_change(self):
        while True:
            color = input("> Enter color (cyan/red/green/blue/magenta/white/menu): ")
            if color == 'cyan':
                COLOR = Fore.CYAN
                print(COLOR + "> Color changed to " + color + " successfully !")
            elif color == 'red':
                COLOR = Fore.RED
                print(COLOR + "> Color changed to " + color + " successfully !")
            elif color == 'green':
                COLOR = Fore.GREEN
                print(COLOR + "> Color changed to " + color + " successfully !")
            elif color == 'blue':
                COLOR = Fore.BLUE
                print(COLOR + "> Color changed to " + color + " successfully !")
            elif color == 'magenta':
                COLOR = Fore.MAGENTA
                print(COLOR + "> Color changed to " + color + " successfully !")
            elif color == 'white':
                COLOR = Fore.WHITE
                print(COLOR + "> Color changed to " + color + " successfully !")
            elif color == 'menu':
                break
            else:
                    print(COLOR + "> Invalid command")

    def get_terminal_size(self):
        return os.get_terminal_size().columns, os.get_terminal_size().lines
