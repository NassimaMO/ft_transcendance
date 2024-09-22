import curses, time, asyncio, aiohttp

ball_symbol = "O"
paddle_symbol = "H"
end = 0

def main(stdscr):
    curses.curs_set(0)   # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(30)   # Set refresh rate (30 milliseconds)
    game = Game()
    game.update(stdscr)

class Game:
    def __init__(self):
        self.site_url = ""
        self.api_key = ""
        self.headers = {""}
        self.pong_table_size = 0
        self.left_paddle = 0
        self.right_paddle = 0
        self.ball = 0
        self.score_left = 0
        self.score_right = 0
        
    def update(self, stdscr):
        while True:
            print("pong")
            break

    def fetch_game_logic():
        print("game logic")

    def display_pong_table(self):
        stdscr.clear()  # Clear the screen
        #stdscr.addstr()  # Draw
        stdscr.refresh()  # Refresh the screen

    def controls(self):
        action = input("> Enter move (up/down/menu): ")
        if action == 'up':
            self.left_paddle += 1
        elif action == 'down':
            self.left_paddle -= 1

    def display_won(self):
        print("won")

    def display_lost(self):
        print("lost")

    def retry_option(self):
        print("retry")