import curses, time

ball_symbol = "O"
paddle_symbol = "H"
paddle_size = 3

def main(stdscr):
    curses.curs_set(0)   # Hide cursor
    stdscr.nodelay(True)   # Non-blocking input
    stdscr.timeout(50)   # Set refresh rate (50 milliseconds)
    game = Game(stdscr)
    game.update()

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.pong_table_size = [60, 16]
        self.middle_y, self.middle_x = self.get_terminal_size()
        self.middle_y = self.middle_y // 2 + self.pong_table_size[1]
        self.middle_x = self.middle_x // 2 + self.pong_table_size[0]
        self.enemy_paddle = [7, 'right']
        self.paddle = [7, 'left']
        self.prev_ball_pos_x = 30
        self.prev_ball_pos_y = 7
        self.ball_pos_x = 30
        self.ball_pos_y = 7
        self.ball_velocity_x = 1 # make it random
        self.ball_velocity_y = 1 # make it random
        self.score = [0, 0]
        
    def update(self):
        self.display_pong_table()
        while True:
            self.get_game_logic()
            self.display_paddles_ball()
            if self.score[0] == 3:
                self.stdscr.addstr(self.center(7, 'y'), self.center(17, 'x'), "You have won !")
                self.stdscr.refresh()
                time.sleep(1)
                break
            elif self.score[1] == 3:
                self.stdscr.addstr(self.center(7, 'y'), self.center(17, 'x'), "You have lost...")
                self.stdscr.refresh()
                time.sleep(1)
                break
            self.controls()

    def display_pong_table(self):
        self.stdscr.clear()
        for x in range(self.pong_table_size[0]):
            self.stdscr.addch(self.center(0, 'y'), self.center(x, 'x'), '-')
            self.stdscr.addch(self.center(self.pong_table_size[1] - 1, 'y'), self.center(x, 'x'), '-') # centering problem stdscr
    
        for y in range(self.pong_table_size[1]):
            self.stdscr.addch(self.center(y, 'y'), self.center(0, 'x'), '|')
            self.stdscr.addch(self.center(y, 'y'), self.center((self.pong_table_size[0] - 1), 'x'), '|')

        self.stdscr.refresh()

    def display_paddles_ball(self):
        for i in range(-1, 2):
            self.stdscr.addch(self.center(self.paddle[0] + i, 'y'), self.center(2, 'x'), paddle_symbol)
            self.stdscr.addch(self.center(self.enemy_paddle[0] + i, 'y'), self.center(self.pong_table_size[0] - 3, 'x'), paddle_symbol)

        self.stdscr.addch(self.center(self.prev_ball_pos_y, 'y'), self.center(self.prev_ball_pos_x, 'x'), ' ')
        self.stdscr.addch(self.center(self.ball_pos_y, 'y'), self.center(self.ball_pos_x, 'x'), ball_symbol)
        self.prev_ball_pos_x = self.ball_pos_x
        self.prev_ball_pos_y = self.ball_pos_y

        self.stdscr.refresh()

    def controls(self):
        #action = await input("> Enter a move (UP/DOWN/MENU): ")
        key = self.stdscr.getch()
        if key == ord('w') and self.paddle[0] > 1:
            self.stdscr.addch(self.center(self.paddle[0] + 1, 'y'), self.center(2, 'x'), ' ')
            self.paddle[0] -= 1
        elif key == ord('s') and self.paddle[0] < 14:
            self.stdscr.addch(self.center(self.paddle[0] - 1, 'y'),  self.center(2, 'x'), ' ')
            self.paddle[0] += 1
        if key == curses.KEY_UP and self.enemy_paddle[0] > 1:
            self.stdscr.addch(self.center(self.enemy_paddle[0] + 1, 'y'),  self.center(self.pong_table_size[0] - 3, 'x'), ' ')
            self.enemy_paddle[0] -= 1
        elif key == curses.KEY_DOWN and self.enemy_paddle[0] < 14:
            self.stdscr.addch(self.center(self.enemy_paddle[0] - 1, 'y'),  self.center(self.pong_table_size[0] - 3, 'x'), ' ')
            self.enemy_paddle[0] += 1

    def get_game_logic(self):
        self.ball_pos_x += self.ball_velocity_x
        self.ball_pos_y += self.ball_velocity_y

        if self.ball_pos_y >= 14 or self.ball_pos_y <= 1:
            self.ball_velocity_y *= -1

        if self.ball_pos_x > 57:
            self.score[0] += 1
            self.stdscr.addstr(self.center(7, 'y'), self.center(24, 'x'), "Point for You !")
            self.stdscr.refresh()
            self.reset()
        elif self.ball_pos_x < 2:
            self.score[1] += 1
            self.stdscr.addstr(self.center(7, 'y'), self.center(17, 'x'), "Point for the enemy...")
            self.stdscr.refresh()
            self.reset()

        if self.is_ball_colliding_with_paddle(self.paddle) or self.is_ball_colliding_with_paddle(self.enemy_paddle):
            self.ball_velocity_x *= -1


    def is_ball_colliding_with_paddle(self, paddle):
        paddle_x = 57 if paddle[1] == 'right' else 2
        paddle_y_min = paddle[0] - 1
        paddle_y_max = paddle[0] + 1

        within_y_bounds = paddle_y_min <= self.ball_pos_y <= paddle_y_max
        within_x_bounds = (paddle_x - 1 <= self.ball_pos_x <= paddle_x + 1)
        
        return within_x_bounds and within_y_bounds

    def reset(self):
        time.sleep(1)
        self.stdscr.addstr(self.center(7, 'y'), self.center(17, 'x'), "                              ")
        for i in range(-1, 2):
            self.stdscr.addch(self.center(self.paddle[0] + i, 'y'),  self.center(2, 'x'), ' ')
            self.stdscr.addch(self.center(self.enemy_paddle[0] + i, 'y'),  self.center(self.pong_table_size[0] - 3, 'x'), ' ')
        self.paddle[0] = 7
        self.enemy_paddle[0] = 7
        self.stdscr.refresh()
        self.ball_pos_x = 30
        self.ball_pos_y = 7
        self.ball_velocity_x *= -1

    def center(self, coord, xy):
        if xy == 'x':
            return self.middle_x + coord
        elif xy == 'y':
            return self.middle_y + coord

    def get_terminal_size(self):
        height, width = self.stdscr.getmaxyx()
        return height, width