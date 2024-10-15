import curses, time

TABLE_SIZE = [60, 16]
MAX_SCORE = 3
BALL_SYMBOL = "O"
BALL_POS = [30, 7]
PADDLE_SYMBOL = "H"
PADDLE_POS = 7
PADDLE_SIZE = 3
WIN = 1
LOSE = 2 

def main(stdscr):
    curses.curs_set(0)   # Hide cursor
    stdscr.nodelay(True)   # Non-blocking input
    stdscr.timeout(50)   # Set refresh rate (50 milliseconds)
    game = Game(stdscr)
    game.update()

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.init_pair(WIN, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(LOSE, curses.COLOR_WHITE, curses.COLOR_RED)
        self.middle_y, self.middle_x = self.get_terminal_size() # take terminal size change into account
        self.middle_y = self.middle_y // 2 - TABLE_SIZE[1] // 2
        self.middle_x = self.middle_x // 2 - TABLE_SIZE[0] // 2
        self.enemy_paddle = [PADDLE_POS, 'right']
        self.paddle = [PADDLE_POS, 'left']
        self.prev_ball_pos_x = BALL_POS[0]
        self.prev_ball_pos_y = BALL_POS[1]
        self.ball_pos_x = BALL_POS[0]
        self.ball_pos_y = BALL_POS[1]
        self.ball_velocity_x = 1 # random
        self.ball_velocity_y = 1 # random
        self.score = [0, 0]
        
    def update(self):
        self.display_pong_table()
        while True:
            self.get_game_logic()
            self.display_ball()
            self.display_paddles()
            self.stdscr.refresh()
            if self.score[0] == MAX_SCORE:
                self.custom_text("You have won !", WIN)
                break
            elif self.score[1] == MAX_SCORE:
                self.custom_text("You have lost...", LOSE)
                break
            self.controls()

    def display_pong_table(self):
        self.stdscr.clear()
        for x in range(TABLE_SIZE[0]):
            self.stdscr.addch(self.center(0, 'y'), self.center(x, 'x'), '-')
            self.stdscr.addch(self.center(TABLE_SIZE[1] - 1, 'y'), self.center(x, 'x'), '-')
    
        for y in range(TABLE_SIZE[1]):
            self.stdscr.addch(self.center(y, 'y'), self.center(0, 'x'), '|')
            self.stdscr.addch(self.center(y, 'y'), self.center((TABLE_SIZE[0] - 1), 'x'), '|')

    def display_paddles(self, paddle_size=PADDLE_SIZE): # might separate ennemy_paddle and paddle
        for i in range(-1, 2): # make it using the paddle size
            self.stdscr.addch(self.center(self.paddle[0] + i, 'y'), self.center(2, 'x'), PADDLE_SYMBOL)
            self.stdscr.addch(self.center(self.enemy_paddle[0] + i, 'y'), self.center(TABLE_SIZE[0] - 3, 'x'), PADDLE_SYMBOL)

    def display_ball(self):
        self.stdscr.addch(self.center(self.prev_ball_pos_y, 'y'), self.center(self.prev_ball_pos_x, 'x'), ' ')
        self.stdscr.addch(self.center(self.ball_pos_y, 'y'), self.center(self.ball_pos_x, 'x'), BALL_SYMBOL)
        self.prev_ball_pos_x = self.ball_pos_x
        self.prev_ball_pos_y = self.ball_pos_y

    def controls(self):
        #action = await input("> Enter a move (UP/DOWN/MENU): ")
        key = self.stdscr.getch()
        if key == ord('w') and self.paddle[0] > 2:
            self.stdscr.addch(self.center(self.paddle[0] + 1, 'y'), self.center(2, 'x'), ' ')
            self.paddle[0] -= 1
        elif key == ord('s') and self.paddle[0] < TABLE_SIZE[1] - 3:
            self.stdscr.addch(self.center(self.paddle[0] - 1, 'y'),  self.center(2, 'x'), ' ')
            self.paddle[0] += 1
        if key == curses.KEY_UP and self.enemy_paddle[0] > 2:
            self.stdscr.addch(self.center(self.enemy_paddle[0] + 1, 'y'),  self.center(TABLE_SIZE[0] - 3, 'x'), ' ')
            self.enemy_paddle[0] -= 1
        elif key == curses.KEY_DOWN and self.enemy_paddle[0] < TABLE_SIZE[1] - 3:
            self.stdscr.addch(self.center(self.enemy_paddle[0] - 1, 'y'),  self.center(TABLE_SIZE[0] - 3, 'x'), ' ')
            self.enemy_paddle[0] += 1

    def get_game_logic(self):
        self.ball_pos_x += self.ball_velocity_x
        self.ball_pos_y += self.ball_velocity_y

        if self.ball_pos_y >= TABLE_SIZE[1] - 2 or self.ball_pos_y <= 1:
            self.ball_velocity_y *= -1

        if self.ball_pos_x > TABLE_SIZE[0] - 2:
            self.score[0] += 1
            self.custom_text("Point for player", WIN)
            self.reset()
        elif self.ball_pos_x < 1:
            self.score[1] += 1
            self.custom_text("Point for enemy_player", LOSE)
            self.reset()

        if self.is_ball_colliding_with_paddle(self.paddle) or self.is_ball_colliding_with_paddle(self.enemy_paddle):
            self.ball_velocity_x *= -1

    def custom_text(self, text, color, t=1):
        self.stdscr.attron(curses.color_pair(color) | curses.A_BOLD)
        self.stdscr.addstr(self.center(-3, 'y'), self.center(TABLE_SIZE[0] // 2 - len(text) // 2 , 'x'), text)
        self.stdscr.attroff(curses.color_pair(color) | curses.A_BOLD)
        self.stdscr.refresh()
        time.sleep(t)
        self.stdscr.addstr(self.center(-3, 'y'), self.center(TABLE_SIZE[0] // 2 - len(text) // 2, 'x'), ' ' * len(text))

    def is_ball_colliding_with_paddle(self, paddle):
        paddle_x = TABLE_SIZE[0] - 2 if paddle[1] == 'right' else 1
        paddle_y_min = paddle[0] - 1
        paddle_y_max = paddle[0] + 1

        within_y_bounds = paddle_y_min <= self.ball_pos_y <= paddle_y_max
        within_x_bounds = (paddle_x - 1 <= self.ball_pos_x <= paddle_x + 1)
        
        return within_x_bounds and within_y_bounds

    def reset(self):
        for i in range(-1, 2):
            self.stdscr.addch(self.center(self.paddle[0] + i, 'y'),  self.center(2, 'x'), ' ')
            self.stdscr.addch(self.center(self.enemy_paddle[0] + i, 'y'),  self.center(TABLE_SIZE[0] - 3, 'x'), ' ')
        self.paddle[0] = PADDLE_POS
        self.enemy_paddle[0] = PADDLE_POS
        self.ball_pos_x = BALL_POS[0]
        self.ball_pos_y = BALL_POS[1]
        self.ball_velocity_x *= -1

    def center(self, coord, xy):
        if xy == 'x':
            return self.middle_x + coord
        elif xy == 'y':
            return self.middle_y + coord

    def get_terminal_size(self):
        height, width = self.stdscr.getmaxyx()
        return height, width