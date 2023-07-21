import sys
print(sys.executable)
import curses
import random
import time


class scoreCount:
    score = 0
    def incr():
        scoreCount.score += 1

class GameWindow:
    window = None

# when using this  don't forget for the char_x to be +1 so it shoots from next to the char
def shoot(char_y,char_x):
    #score = 0
    for i in range(3):
        if (char_x+i < width_window-1):
            window.addch(char_y,char_x+i,'a')
            if (monster_y == char_y and monster_x == char_x+i):
                curses.flash()
                scoreCount.incr()
                window.addstr(0,1,f"Score:{scoreCount.score}")
            window.refresh()
            time.sleep(0.5)
            window.addch(char_y,char_x+i,' ')

def monster(char_y, char_x):
    global monster_y
    global monster_x
    monster_y = random.randint(2,height_window-2)
    monster_x = random.randint(2,width_window-2)
    if (monster_y == char_y):
        monster_y = random.randint(monster_y+1, height_window-2)
    elif (monster_x == char_x):
        monster_x = random.randint(monster_x+1, width_window-2)
    window.addch(monster_y,monster_x,'T')

class GameState:
    pass


def main():
    curses.initscr()
    # disable reading keys to the screen
    curses.noecho()
    # respond without entering enter key
    curses.cbreak()
    global height_window
    global width_window
    height_window = 6
    width_window = 30
    char_x = 15
    char_y = 3
    global window 
    window = curses.newwin(height_window,width_window)
    window.box()
    window.addstr(0,1,f"Score:0")
    curses.curs_set(0)
    monster(char_y,char_x)
    while True:
        window.addch(char_y,char_x,'A')
        # this already refreshes for us
        c = window.getch()
        window.addch(char_y,char_x,' ')
        window.refresh()
        if (c == ord('d')):
            if (char_x < width_window-2):
                char_x += 1
            else:
                curses.beep()
        elif (c == ord('a')):
            if (char_x > 1):
                char_x -= 1
            else:
                curses.beep()
        elif (c == ord('w')):
            if (char_y > 1):
                char_y -= 1
            else:
                curses.beep()
        elif (c == ord('s')):
            if (char_y < height_window-2):
                char_y += 1
            else:
                curses.beep()
        elif (c == ord(' ')):
            shoot(char_y,char_x+1)

        elif (c == ord('q')):
            break







    # refresh is needed to update the screen after you update variables
    # window.refresh()

    # can use curs_set(False) to suppress the blinking cursor
    # getch() refreshes the screen and waits for the user to hit a key
    # c = stdscr.getch() and c == ord(letter press)




    # end operation to finish a program
    curses.nocbreak()
    curses.echo()
    curses.endwin()
  

if __name__ == "__main__":
    main()