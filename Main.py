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

class Player:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y

# keeps track of the game world in a 2d grid
class World:
    def __init__(self, player_start_x, player_start_y, max_x, max_y):
        self.player = Player(player_start_x, player_start_y)
        self.max_x = max_x
        self.max_y = max_y
    
# keeps track of variables that change frequently due to user choice, like user coordinate and etc.
class GameState:
    def __init__(self, window_max_x, window_max_y):
        # TODO: starting with a world whose size is the same as the window, but later it should
        # be made bigger (so we can move around)
        self.world = World(15, 3, window_max_x, window_max_y)
        self.hit = False

# function that decides if the user's gun reaches the enemy. If it does it updates the score variable.
def shoot_pistol(state, window_info, count):
    player = state.world.player
    temp_x = (state.world.player.x + 1)
    for i in range(3):
        if ((temp_x + i) < (window_info.width_window - 1)):
            window_info.window.addch(player.y, temp_x + i, 'a')
            if (state.monster_y == player.y and state.monster_x == (temp_x + i)):
                curses.flash()
                count.incr()
                window_info.window.addstr(0, 9, f"Score:{count.score}")
                state.hit = True
            window_info.window.refresh()
            time.sleep(0.5)
            window_info.window.addch(player.y, temp_x + i, ' ')

# creates a monster at a random location on the map
def create_monster(state, window_info):
    player = state.world.player
    state.monster_y = random.randint(2, window_info.height_window - 2)
    state.monster_x = random.randint(2, window_info.width_window - 2)
    if (state.monster_y == player.y):
        state.monster_y = random.randint(1, window_info.height_window - 2)
        while (state.monster_y == player.y):
            state.monster_y = random.randint(1, window_info.height_window - 2)
    elif (state.monster_x == player.x):
        state.monster_x = random.randint(1, window_info.width_window - 2)
        while (state.monster_x == player.x):
            state.monster_x = random.randint(1, window_info.width_window - 2)
    window_info.window.addch(state.monster_y, state.monster_x, 'T')


def main():
    window_info = GameWindow()
    game_state = GameState(window_info.height_window, window_info.width_window)
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

    # main game loop
    while True:
        player = game_state.world.player
        window_info.window.addch(player.y, player.x, 'A')
        if (game_state.monster_x == player.x and game_state.monster_y == player.y):
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
        window_info.window.addch(player.y, player.x, ' ')
        window_info.window.refresh()
        if (c == ord('d')):
            if (player.x < window_info.width_window - 2):
                player.x += 1
            else:
                curses.beep()
        elif (c == ord('a')):
            if (player.x > 1):
                player.x -= 1
            else:
                curses.beep()
        elif (c == ord('w')):
            if (player.y > 1):
                player.y -= 1
            else:
                curses.beep()
        elif (c == ord('s')):
            if (player.y < window_info.height_window - 2):
                player.y += 1
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