import curses
import random
import time

# keeps track of universal score and health
class Statistics:
    score = 0
    health = 3
    def incr():
        Statistics.score += 1
    def decr():
        Statistics.health -= 1
    

# keeps track of any variable relating to the window of 
# the game
class GameWindow:
    window = None
    height_window = 6
    width_window = 30

# keeps track of variables that change frequently due to user choice, like user coordinate and etc.
class GameState:
    char_x = 15
    char_y = 3

# function that decides if the user's gun reaches the enemy. If it does it updates the score variable
def shoot(state, window, count):
    temp_x = state.char_x+1
    for i in range(3):
        if (temp_x+i < window.width_window-1):
            window.window.addch(state.char_y,temp_x+i,'a')
            if (state.monster_y == state.char_y and state.monster_x == temp_x+i):
                curses.flash()
                count.incr()
                window.window.addstr(0,9,f"Score:{count.score}")
            window.window.refresh()
            time.sleep(0.5)
            window.window.addch(state.char_y,temp_x+i,' ')

# creates a monster at a random location on the map
def monster(state, window):
    state.monster_y = random.randint(2,window.height_window-2)
    state.monster_x = random.randint(2,window.width_window-2)
    if (state.monster_y == state.char_y):
        state.monster_y = random.randint(state.monster_y+1, window.height_window-2)
    elif (state.monster_x == state.char_x):
        state.monster_x = random.randint(state.monster_x+1, window.width_window-2)
    window.window.addch(state.monster_y,state.monster_x,'T')


def main(state, window_info, count):
    curses.initscr()
    # disable reading keys to the screen
    curses.noecho()
    # respond without entering enter key
    curses.cbreak()
    window_info.window = curses.newwin(window_info.height_window,window_info.width_window)
    window_info.window.box()
    window_info.window.addstr(0,9,"Score:0")
    window_info.window.addstr(0,1,"Lives:3")
    curses.curs_set(0)
    monster(GameState,GameWindow)
    while True:
        window_info.window.addch(state.char_y,state.char_x,'A')
        if (state.monster_x == state.char_x and state.monster_y == state.char_y):
            count.decr()
            window_info.window.addstr(0,1,f"Lives:{count.health}")
            window_info.window.refresh()
            if (count.health == 0):
                window_info.window.addstr(2,10,f"YOU LOSE!")
                window_info.window.refresh()
                time.sleep(1.5)
                exit()
        c = window_info.window.getch()
        window_info.window.addch(state.char_y,state.char_x,' ')
        window_info.window.refresh()
        if (c == ord('d')):
            if (state.char_x < window_info.width_window-2):
                state.char_x += 1
            else:
                curses.beep()
        elif (c == ord('a')):
            if (state.char_x > 1):
                state.char_x -= 1
            else:
                curses.beep()
        elif (c == ord('w')):
            if (state.char_y > 1):
                state.char_y -= 1
            else:
                curses.beep()
        elif (c == ord('s')):
            if (state.char_y < window_info.height_window-2):
                state.char_y += 1
            else:
                curses.beep()
        elif (c == ord(' ')):
            shoot(GameState, GameWindow, Statistics)
            # if (GameState.hit == True):
            #     monster()
            # GameState.hit = False
        elif (c == ord('q')):
            break
    # lines that end operation to finish a program
    curses.nocbreak()
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    main(GameState,GameWindow,Statistics)


# Comments:
    # refresh is needed to update the screen after you update variables
    # window.refresh()
    # can use curs_set(False) to suppress the blinking cursor
    # getch() refreshes the screen and waits for the user to hit a key
    # c = stdscr.getch() and c == ord(letter press)
    
    # import sys
    # print(sys.executable)   
    # the two lines above help you see the path of your system so if your debugger is on the wrong
    # path it will not run