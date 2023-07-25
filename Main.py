import curses
import random
import time

# TODO - stop using specific numbers like 6, 30 as much as possible
# TODO - see if we can draw the box ourselves so we can have more control over the window
#         ex. we want to write lines of text below the 'box', right now we can't because curses assumes a border on the edge
# TODO - OR come up with a place to put text so we can expand debug info
# TODO - make the bullet a World Object
# TODO - get rid of the 'hidden' walls that are BORDER of the screen (they need to be in world space)

# renders the window we are currently are at
class Renderer:
    def __init__(self):
        pass

    def render(self, state):
        window = state.window
        stats = state.stats
        debug_info = state.debug_info
        player = state.world.player
        monster = state.world.monster
        
        window.clear()
        window.box()

        stats._render(state)
        player._render(state)
        monster._render(state)
        debug_info._render(state)

        # TODO - Move bullet here

        window.refresh()


class ScreenPos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WorldPos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WorldObject:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        self.pos = WorldPos(start_x, start_y)

    @property
    def x(self):
        return self.pos.x
    
    @x.setter
    def x(self, x):
        self.pos.x = x
    
    @property
    def y(self):
        return self.pos.y
    
    @y.setter
    def y(self, y):
        self.pos.y = y

#  player.pos.x
#  player.pos.getX()
#  player.x <- want and want to share with Monster
#    

# keeps track of player position on world
class Player(WorldObject):
    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y)

    def _render(self, state):
        screen_pos = state.camera.to_screen_space(self.pos)
        state.window.addch(screen_pos.y, screen_pos.x, 'A')

# keeps track of the game world in a 2d grid
class World:
    def __init__(self, player_start_x, player_start_y, max_x, max_y):
        self.player = Player(player_start_x, player_start_y)
        self.max_x = max_x
        self.max_y = max_y
        self.monster = Monster()
        self.bullet = None

# keeps track of the current 'camera' position over the 2d world in world space
class Camera:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y

    def to_screen_space(self, world_pos):
        return ScreenPos(world_pos.x + self.x, world_pos.y + self.y)

# keeps track of variables that change frequently due to user choice, like user coordinate and etc.
class GameState:
    # pass in 30 for x and 6 for y  
    def __init__(self, window_max_y, window_max_x):
        self.quit = False
        # TODO: starting with a world whose size is the same as the window, but later it should
        # be made bigger (so we can move around)
        
        default_start_x = 15
        default_start_y = 3

        self.world = World(default_start_x, default_start_y, window_max_x, window_max_y)
        self.window = None
        self.stats = Statistics()
        self.renderer = Renderer()
        self.camera = Camera(0, 0)
        self.debug_info = DebugInfo()

    # can get rid of monster and renderer here
    def run(self):
        self.world.monster.create_monster(self)
        while not self.quit:
            player = self.world.player
            monster = self.world.monster

            self.run_bullet_manager()
            if (monster.x == player.x and monster.y == player.y):
                self.stats.lives_state(self, self.renderer)

            self.process_game_moves()

            self.renderer.render(self)

    def process_game_moves(self):
        window = self.window
        world = self.world
        player = self.world.player
        camera = self.camera

        c = window.getch()
        if (c == ord('d')):
            if (player.x < world.max_x - 2):
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
            if (player.y < world.max_y - 2):
                player.y += 1
            else:
                curses.beep()
        elif (c == ord(' ')):
            self.world.bullet = Bullet(player.x, player.y)
            self.world.bullet.shoot(self)
        elif (c == ord('m')):
            self.debug_info.show = not self.debug_info.show
        elif (c == ord('q')):
            self.quit = True
        # TODO - should these only be available in certain cases like if debug info is shown?
        elif (c == ord('k')):
            camera.x += 1
        elif (c == ord('h')):
            camera.x -= 1
        elif (c == ord('u')):
            camera.y -= 1
        elif (c == ord('j')):
            camera.y += 1

    def run_bullet_manager(self):
        if self.world.bullet and not self.world.bullet.valid:
            self.world.bullet = None

class DebugInfo():
    def __init__(self):
        self.show = False
    
    def _render(self, state):
        player = state.world.player
        if self.show:
            # player world pos

            state.window.addstr(0, 15, f"wpos:{player.y}, {player.x}")

# stats of the user in the game
class Statistics:
    def __init__(self):
        self.score = 0
        self.health = 3

    def incr_score(self):
        self.score += 1

    def decr_health(self):
        self.health -= 1

    def lives_state(self, state, render):
        window = state.window
        monster = state.world.monster
        self.decr_health()

        if (self.health != 0):
            monster.create_monster(state)

        # TODO - Render!
        window.addstr(0, 1, f"Lives:{self.health}")
        window.refresh()

        if (self.health == 0):
            render.render(state)
            window.addstr(2, 10, f"YOU LOSE!")
            window.refresh()
            time.sleep(1.5)
            exit()

    def _render(self, state):
        window = state.window
        window.addstr(0, 9, f"Score:{self.score}")
        window.addstr(0, 1, f"Lives:{self.health}")

# bullet operations of the user
class Bullet:
    def __init__(self, start_x, start_y):
        # Add 1 so we spawn next to the player 
        self.x = start_x + 1
        self.y = start_y
        self.valid = True
    
    def _render(self, state):
        pos = state.camera.to_screen_space(self.x, self.y)
        state.window.addch(pos[1], pos[0], 'a')

    # need to delete this later
    def shoot(self, state):
        player = state.world.player
        world = state.world
        stats = state.stats
        monster = state.world.monster
        renderer = state.renderer

        temp_x = (state.world.player.x + 1)

        # TODO - Move this to render in the renderer
        for i in range(3):
            if ((temp_x + i) < (world.max_x - 1)):
                self.x = temp_x + i
                self.render(state)
                if (monster.y == self.y and monster.x == self.x):
                    monster.create_monster(state)
                    curses.flash()
                    stats.incr_score()
                state.window.refresh()
                time.sleep(0.5)
                renderer.render(state)
        
        self.valid = False

class Monster(WorldObject):
    def __init__(self):
        # TODO - we need to either pass this in or do something different so 
        # it's not static.
        super().__init__(5, 5)

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
    def _render(self, state):
        screen_pos = state.camera.to_screen_space(self.pos)
        state.window.addch(screen_pos.y, screen_pos.x, 'T')

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

    render = Renderer()
    render.render(game_state)
    game_state.run()

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