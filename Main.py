import curses
import random
import time

# keeps track of universal score and health.
class Statistics:
    def __init__(self):
        self.score = 0
        self.health = 3
    def incr(self):
        self.score += 1
    def decr(self):
        self.health -= 1
    

# keeps track of any variable relating to the window of the game.
class GameWindow:
    def __init__(self):
        self.window = None
        self.height_window = 6
        self.width_window = 30

# keeps track of variables that change frequently due to user choice, like user coordinate and etc.
class GameState:
    def __init__(self):
        self.char_x = 15
        self.char_y = 3
        self.hit = False

# function that decides if the user's gun reaches the enemy. If it does it updates the score variable.
def shoot_pistol(state, window_info, count):
    temp_x = (state.char_x + 1)
    for i in range(3):
        if ((temp_x + i) < (window_info.width_window - 1)):
            window_info.window.addch(state.char_y, temp_x + i, 'a')
            if (state.monster_y == state.char_y and state.monster_x == (temp_x + i)):
                curses.flash()
                count.incr()
                window_info.window.addstr(0, 9, f"Score:{count.score}")
                state.hit = True
            window_info.window.refresh()
            time.sleep(0.5)
            window_info.window.addch(state.char_y, temp_x + i, ' ')

# creates a monster at a random location on the map
def create_monster(state, window_info):
    state.monster_y = random.randint(2, window_info.height_window - 2)
    state.monster_x = random.randint(2, window_info.width_window - 2)
    if (state.monster_y == state.char_y):
        state.monster_y = random.randint(1, window_info.height_window - 2)
        while (state.monster_y == state.char_y):
            state.monster_y = random.randint(1, window_info.height_window - 2)
    elif (state.monster_x == state.char_x):
        state.monster_x = random.randint(1, window_info.width_window - 2)
        while (state.monster_x == state.char_x):
            state.monster_x = random.randint(1, window_info.width_window - 2)
    window_info.window.addch(state.monster_y, state.monster_x, 'T')


def main():
    game_state = GameState()
    window_info = GameWindow()
    stats_info = Statistics()
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    window_info.window = curses.newwin(window_info.height_window, window_info.width_window)
    window_info.window.box()
    window_info.window.addstr(0,9,"Score:0")
    window_info.window.addstr(0,1,"Lives:3")
    curses.curs_set(0)
    create_monster(game_state, window_info)
    while True:
        window_info.window.addch(game_state.char_y, game_state.char_x, 'A')
        if (game_state.monster_x == game_state.char_x and game_state.monster_y == game_state.char_y):
            stats_info.decr()
            if (stats_info.health != 0):
                create_monster(game_state, window_info)
            window_info.window.addstr(0,1,f"Lives:{stats_info.health}")
            window_info.window.refresh()
            if (stats_info.health == 0):
                window_info.window.addstr(2, 10, f"YOU LOSE!")
                window_info.window.refresh()
                time.sleep(1.5)
                exit()
        c = window_info.window.getch()
        window_info.window.addch(game_state.char_y, game_state.char_x, ' ')
        window_info.window.refresh()
        if (c == ord('d')):
            if (game_state.char_x < window_info.width_window - 2):
                game_state.char_x += 1
            else:
                curses.beep()
        elif (c == ord('a')):
            if (game_state.char_x > 1):
                game_state.char_x -= 1
            else:
                curses.beep()
        elif (c == ord('w')):
            if (game_state.char_y > 1):
                game_state.char_y -= 1
            else:
                curses.beep()
        elif (c == ord('s')):
            if (game_state.char_y < window_info.height_window - 2):
                game_state.char_y += 1
            else:
                curses.beep()
        elif (c == ord(' ')):
            shoot_pistol(game_state, window_info, stats_info)
            if (game_state.hit == True):
                create_monster(game_state, window_info)
            game_state.hit = False
        elif (c == ord('q')):
            break
    curses.nocbreak()
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    main()


# Comments:
    # refresh is needed to update the screen after you update variables
    # window.refresh()
    # can use curs_set(False) to suppress the blinking cursor
    # getch() refreshes the screen and waits for the user to hit a key
    # c = stdscr.getch() and c == ord(letter press)
    # curses.noecho() disables reading keys to the screen
    # curses.cbreak() makes it so console responds without pressing enter key

    # three lines used to end console run
    # curses.nocbreak()
    # curses.echo()
    # curses.endwin()
    
    # import sys
    # print(sys.executable)   
    # the two lines above help you see the path of your system so if your debugger is on the wrong
    # path it will not run