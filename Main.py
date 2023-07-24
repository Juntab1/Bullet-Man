import curses
import random
import time

# renders the window we are currently are at
class Render:
    def __init__(self):
        pass
    def render(self, state, monster):
        window = state.window
        stats = state.stats
        player = state.world.player
        window.clear()
        window.box()
        stats.render(state)
        player.render(state)
        monster.render(state)
        window.refresh()

# keeps track of player position on world
class Player:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y

    def render(self, state):
        state.window.addch(self.y, self.x, 'A')

# keeps track of the game world in a 2d grid
class World:
    def __init__(self, player_start_x, player_start_y, max_x, max_y):
        self.player = Player(player_start_x, player_start_y)
        self.max_x = max_x
        self.max_y = max_y
    
# keeps track of variables that change frequently due to user choice, like user coordinate and etc.
class GameState:
    # pass in 30 for x and 6 for y  
    def __init__(self, window_max_y, window_max_x):
        # TODO: starting with a world whose size is the same as the window, but later it should
        # be made bigger (so we can move around)
        self.world = World(15, 3, window_max_x, window_max_y)
        self.window = None
        self.stats = Statistics()
    def reg_operation(self, monster, render):
        while True:
            player = self.world.player
            if (monster.x == player.x and monster.y == player.y):
                # can we pass in self like this?
                self.stats.lives_state(monster, self, render)
            # TODO - can we clear the window and re-draw everything at current position
            # instead of trying the complicated dance of setting their pos to " "
            render.render(self, monster)
            # read input
            window = self.window
            world = self.world
            # read input
            c = window.getch()
            if (c == ord('d')):
                if (player.x < self.world.max_x - 2):
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
                if (player.y < self.world.max_y - 2):
                    player.y += 1
                else:
                    curses.beep()
            elif (c == ord(' ')):
                bullet = Bullet(player.y, player.x)
                bullet.shoot(self,monster,render)
            elif (c == ord('q')):
                break

# stats of the user in the game
class Statistics:
    def __init__(self):
        self.score = 0
        self.health = 3
    def incr_score(self):
        self.score += 1
    def decr_health(self):
        self.health -= 1
    def lives_state(self, monster, state, render):
        window = state.window
        self.decr_health()
        if (self.health != 0):
            monster.create_monster(state)
        window.addstr(0,1,f"Lives:{self.health}")
        window.refresh()
        if (self.health == 0):
            render.render(state,monster)
            window.addstr(2, 10, f"YOU LOSE!")
            window.refresh()
            time.sleep(1.5)
            exit()
    def render(self, state):
        window = state.window
        window.addstr(0,9,f"Score:{self.score}")
        window.addstr(0,1,f"Lives:{self.health}")

# bullet operations of the user
class Bullet:
    def __init__(self,start_y,start_x):
        self.x = start_x
        self.y = start_y
    
    def render(self, state):
        state.window.addch(self.y, self.x, 'a')

    # need to delete this later
    def shoot(self, state, monster, render):
        player = state.world.player
        world = state.world
        stats = state.stats
        temp_x = (state.world.player.x + 1)
        for i in range(3):
            if ((temp_x + i) < (world.max_x - 1)):
                self.x = temp_x + i
                #TODO - would be great to replace the 'bullet' with a class
                # that is unrelated to the player and maintain's it's own x, and y.
                # then we can have a bullet.render() on that class and disconnect
                # it from the position of the player in this function.
                
                # do render here instead of doing the window.addch
                self.render(state)
                if (monster.y == self.y and monster.x == self.x):
                    monster.create_monster(state)
                    curses.flash()
                    stats.incr_score()
                state.window.refresh()
                time.sleep(0.5)
                render.render(state,monster)

class Monster:
    def __init__(self):
        self.y = 5
        self.x = 5

    # creates a monster at a random location on the map
    def create_monster(self, state):
        world = state.world
        player = state.world.player
        self.y = random.randint(2, world.max_y - 2)
        self.x = random.randint(2, world.max_x - 2)
        if (self.y == player.y):
            self.y = random.randint(1, world.max_y - 2)
            while (self.y == player.y):
                self.y = random.randint(1, world.max_y - 2)
        elif (self.x == player.x):
            self.x = random.randint(1, world.max_x - 2)
            while (self.x == player.x):
                self.x = random.randint(1, world.max_x - 2)
    
    # renders the monster on the screen
    def render(self, state):
        state.window.addch(self.y, self.x, 'T')
    # this is going to be nessesary for when we move the monster toward the player
    # def move_monster(self, state, window_info):
    #     if ((self.monster_y == state.char_y)):
    #         for i in range(2):
    #             if (self.monster_y > 1 and self.monster_y < window_info.height_window - 2):
    #                 self.monster_y 
    #     elif ((self.monster_x == state.char_x)):


def main():
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    # later have to put world length inside of it instead of just window
    game_state = GameState(6, 30)
    game_state.window = curses.newwin(6, 30)
    player = game_state.world.player
    render = Render()
    monster = Monster()
    monster.create_monster(game_state)
    render.render(game_state, monster)
    # main game loop
    game_state.reg_operation(monster, render)
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