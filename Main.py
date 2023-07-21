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

# keeps track of variables that change frequently due to user choice, like user coordinate and etc.
class GameState:
    pass

# function that decides if the user's gun reaches the enemy. If it does it updates the score variable
def shoot():
    temp_x = GameState.char_x+1
    for i in range(3):
        if (temp_x+i < GameWindow.width_window-1):
            GameWindow.window.addch(GameState.char_y,temp_x+i,'a')
            if (GameState.monster_y == GameState.char_y and GameState.monster_x == temp_x+i):
                curses.flash()
                Statistics.incr()
                GameWindow.window.addstr(0,9,f"Score:{Statistics.score}")
            GameWindow.window.refresh()
            time.sleep(0.5)
            GameWindow.window.addch(GameState.char_y,temp_x+i,' ')

# creates a monster at a random location on the map
def monster():
    GameState.monster_y = random.randint(2,GameWindow.height_window-2)
    GameState.monster_x = random.randint(2,GameWindow.width_window-2)
    if (GameState.monster_y == GameState.char_y):
        GameState.monster_y = random.randint(GameState.monster_y+1, GameWindow.height_window-2)
    elif (GameState.monster_x == GameState.char_x):
        GameState.monster_x = random.randint(GameState.monster_x+1, GameWindow.width_window-2)
    GameWindow.window.addch(GameState.monster_y,GameState.monster_x,'T')


def main():
    curses.initscr()
    # disable reading keys to the screen
    curses.noecho()
    # respond without entering enter key
    curses.cbreak()
    GameWindow.height_window = 6
    GameWindow.width_window = 30
    GameState.char_x = 15
    GameState.char_y = 3
    GameWindow.window = curses.newwin(GameWindow.height_window,GameWindow.width_window)
    GameWindow.window.box()
    GameWindow.window.addstr(0,9,"Score:0")
    GameWindow.window.addstr(0,1,"Lives:3")
    curses.curs_set(0)
    monster()
    while True:
        GameWindow.window.addch(GameState.char_y,GameState.char_x,'A')
        if (GameState.monster_x == GameState.char_x and GameState.monster_y == GameState.char_y):
            Statistics.decr()
            GameWindow.window.addstr(0,1,f"Lives:{Statistics.health}")
            GameWindow.window.refresh()
            if (Statistics.health == 0):
                GameWindow.window.addstr(2,10,f"YOU LOSE!")
                GameWindow.window.refresh()
                time.sleep(1.5)
                exit()
        c = GameWindow.window.getch()
        GameWindow.window.addch(GameState.char_y,GameState.char_x,' ')
        GameWindow.window.refresh()
        if (c == ord('d')):
            if (GameState.char_x < GameWindow.width_window-2):
                GameState.char_x += 1
            else:
                curses.beep()
        elif (c == ord('a')):
            if (GameState.char_x > 1):
                GameState.char_x -= 1
            else:
                curses.beep()
        elif (c == ord('w')):
            if (GameState.char_y > 1):
                GameState.char_y -= 1
            else:
                curses.beep()
        elif (c == ord('s')):
            if (GameState.char_y < GameWindow.height_window-2):
                GameState.char_y += 1
            else:
                curses.beep()
        elif (c == ord(' ')):
            shoot()
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
    main()


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