import curses
import random
import time


class ScoreCount:
    score = 0
    def incr():
        ScoreCount.score += 1

class Lives:
    health = 3
    def decr():
        Lives.health -= 1

class GameWindow:
    window = None

class GameState:
    pass

# when using this  don't forget for the char_x to be +1 so it shoots from next to the char
def shoot():
    #score = 0
    temp_x = GameState.char_x+1
    for i in range(3):
        if (temp_x+i < GameWindow.width_window-1):
            GameWindow.window.addch(GameState.char_y,temp_x+i,'a')
            if (GameState.monster_y == GameState.char_y and GameState.monster_x == temp_x+i):
                curses.flash()
                ScoreCount.incr()
                GameWindow.window.addstr(0,1,f"Score:{ScoreCount.score}")
            GameWindow.window.refresh()
            time.sleep(0.5)
            GameWindow.window.addch(GameState.char_y,temp_x+i,' ')

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
        # this is where the life if statement is going to be to decrement the life counter
        # this already refreshes for us
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

        elif (c == ord('q')):
            break
    # end operation to finish a program
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