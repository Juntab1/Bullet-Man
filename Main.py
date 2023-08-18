import curses
import random
import time

# TODO - stop using specific numbers like 6, 30 as much as possible
# TODO - there is an error for some reason where if you move one way the monster moves with you too
# TODO - see if we can draw the box ourselves so we can have more control over the window
#         ex. we want to write lines of text below the 'box', right now we can't because curses assumes a border on the edge
# TODO - OR come up with a place to put text so we can expand debug info


# 2. create different levels of monsters


# Utility functions not associated with a class

def point_in_rect(rx1, ry1, rx2, ry2, x, y):
    """
        Given a rectangle from bottom-left (rx1, ry1) to upper-right (rx2, ry2), 
        see if point (x, y) is inside of it
    """
    if (x > (rx1) and x < (rx2 - 1) and
        y > (ry1) and y < (ry2 - 1)) :
        return True
    else :
        return False
    
def get_rect_from_center(x, y, w, h):
    return ((int(x - w/2), int(y - h/2)), (int(x + w/2), int(y + h/2)))

# renders the window we are currently are at
class Renderer:
    def __init__(self):
        pass

    def render(self, state):
        window = state.window
        stats = state.stats
        debug_info = state.debug_info
        world = state.world
        player = state.world.player
        monsters = state.world.monsters
        trees = state.world.trees
        bullet = state.world.bullet
        
        
        window.clear()
        window.box()

        world._render(state)
        stats._render(state)
        debug_info._render(state)
        
        player._render(state)

        for i in range(len(monsters)):
            # make random location x and y for trees here
            monsters[i]._render(state)

        for i in range(len(trees)):
            # make random location x and y for trees here
            trees[i]._render(state)


        if bullet:
            bullet._render(state)

        window.refresh()


class ScreenPos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WorldPos:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# thought I have currently is that I can get rid of the start_x and start_y because I just manually put in 
# the number of whatever is half of the screen size. The player is created first and everything elses position is randomized
# so that way we could get rid of like 10 lines of code total but the problem would be how am I going to connect the half screen size with
# this class

# solution is in main just create world object and pass in the parameters needed 

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
#    

# keeps track of player position on world
class Player(WorldObject):
    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y)
        self.start_x = start_x
        self.start_y = start_y

    def _render(self, state):
        camera = state.camera
        
        if camera.is_visible(self.pos):
            screen_pos = state.camera.to_screen_space(self.pos)
            state.window.addch(screen_pos.y, screen_pos.x, 'A')
        else:
            return
        
class Wall(WorldObject):
    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y)
        self.start_x = start_x
        self.start_y = start_y


# keeps track of the game world in a 2d grid
class World:
    def __init__(self, player_start_x, player_start_y, max_x, max_y, world_x_compare_window, world_y_compare_window, window_max_x, window_max_y):
        self.common_tools = CommonTools()
        self.player = Player(player_start_x, player_start_y)
        self.monster = Monster()
        self.bullet = None

        self.max_x = max_x
        self.max_y = max_y
        self.window_max_x = window_max_x
        self.window_max_y = window_max_y
        self.world_x_compare_window = int(world_x_compare_window)
        self.world_y_compare_window = int(world_y_compare_window)


        self.trees = []
        for i in range(30):
            tree = Tree()
            # later if I wanted to I could get rid of this first random variable creation by starting all trees at the position of the players start position
            # also, I don't make sure if each tree is overlapping but that does not seem as important as only checking the player and monster position 
            tree.x = random.randint(-self.world_x_compare_window, self.world_x_compare_window + self.window_max_x)
            tree.y = random.randint(-self.world_y_compare_window, self.world_y_compare_window + self.window_max_y)
            while(not self.common_tools.object_clash(tree, self.player.x, self.player.y)):
                tree.x = random.randint(-self.world_x_compare_window, self.world_x_compare_window + self.window_max_x)
                tree.y = random.randint(-self.world_y_compare_window, self.world_y_compare_window + self.window_max_y)
            self.trees.append(tree)
        
        self.monsters = []
        for i in range(3):
            monster = Monster()
            monster.x = random.randint(-self.world_x_compare_window, self.world_x_compare_window + self.window_max_x)
            monster.y = random.randint(-self.world_y_compare_window, self.world_y_compare_window + self.window_max_y)
            while(not self.common_tools.object_clash(monster, self.player.x, self.player.y)):
                monster.x = random.randint(-self.world_x_compare_window, self.world_x_compare_window + self.window_max_x)
                monster.y = random.randint(-self.world_y_compare_window, self.world_y_compare_window + self.window_max_y)
                for i in range(len(self.trees)):
                    while(not self.common_tools.object_clash(monster, self.trees[i].x, self.trees[i].y)):
                        monster.x = random.randint(-self.world_x_compare_window, self.world_x_compare_window + self.window_max_x)
                        monster.y = random.randint(-self.world_y_compare_window, self.world_y_compare_window + self.window_max_y)
            self.monsters.append(monster)

        self.left_wall_middle = Wall(-self.world_x_compare_window - 1, player_start_y)
        self.left_wall_top = Wall(-self.world_x_compare_window - 1, -self.world_y_compare_window - 1)
        self.left_wall_bottom = Wall(-self.world_x_compare_window - 1, self.window_max_y + self.world_y_compare_window + 1)

        self.right_wall_middle = Wall(self.window_max_x + self.world_x_compare_window + 1, player_start_y)
        self.right_wall_top = Wall(self.window_max_x + self.world_x_compare_window + 1, -self.world_y_compare_window - 1)
        self.right_wall_bottom = Wall(self.window_max_x + self.world_x_compare_window + 1, self.window_max_y + self.world_y_compare_window + 1)

        self.bottom_wall_middle = Wall(player_start_x, self.window_max_y + self.world_y_compare_window + 1)
        self.bottom_wall_middle_right = Wall(player_start_x + 4, self.window_max_y + self.world_y_compare_window + 1)
        self.bottom_wall_middle_left = Wall(player_start_x - 4, self.window_max_y + self.world_y_compare_window + 1)
        self.bottom_wall_right = Wall(self.window_max_x + self.world_x_compare_window + 1, self.window_max_y + self.world_y_compare_window + 1)
        self.bottom_wall_left = Wall(-self.world_x_compare_window - 1, self.window_max_y + self.world_y_compare_window + 1)

        self.top_wall_middle = Wall(player_start_x, -self.world_y_compare_window - 1)
        self.top_wall_middle_right = Wall(player_start_x + 4, -self.world_y_compare_window - 1)
        self.top_wall_middle_left = Wall(player_start_x - 4, -self.world_y_compare_window - 1)
        self.top_wall_right = Wall(self.window_max_x + self.world_x_compare_window + 1, -self.world_y_compare_window - 1)
        self.top_wall_left = Wall(-self.world_x_compare_window - 1, -self.world_y_compare_window - 1)


    def _render(self, state):
        camera = state.camera

        # left wall
        if camera.is_visible(self.left_wall_top.pos):
            screen_pos = state.camera.to_screen_space(self.left_wall_top.pos)
            for i in range(camera.height - 2):
                if (screen_pos.y + i < camera.height - 1 and screen_pos.x > 0):
                    state.window.addch(screen_pos.y + i, screen_pos.x, '*')
        elif camera.is_visible(self.left_wall_bottom.pos):
            screen_pos = state.camera.to_screen_space(self.left_wall_bottom.pos)
            for i in range(camera.height - 2):
                if (screen_pos.y > i and screen_pos.x > 0):
                    state.window.addch(1 + i, screen_pos.x, '*')
        elif camera.is_visible(self.left_wall_middle.pos):
            screen_pos = state.camera.to_screen_space(self.left_wall_middle.pos)
            for i in range(camera.height - 2):
                if (screen_pos.x > 0):
                    state.window.addch(1 + i, screen_pos.x, '*')
            
        # right wall
        if camera.is_visible(self.right_wall_top.pos):
            screen_pos = state.camera.to_screen_space(self.right_wall_top.pos)
            for i in range(camera.height - 2):
                if (screen_pos.y + i < camera.height - 1 and screen_pos.x < self.window_max_x - 1):
                    state.window.addch(screen_pos.y + i, screen_pos.x, '*')
        elif camera.is_visible(self.right_wall_bottom.pos):
            screen_pos = state.camera.to_screen_space(self.right_wall_bottom.pos)
            for i in range(camera.height - 2):
                if (screen_pos.y > i and screen_pos.x < self.window_max_x - 1):
                    state.window.addch(1 + i, screen_pos.x, '*')
        elif camera.is_visible(self.right_wall_middle.pos):
            screen_pos = state.camera.to_screen_space(self.right_wall_middle.pos)
            for i in range(camera.height - 2):
                if (screen_pos.x < self.window_max_x - 1):
                    state.window.addch(1 + i, screen_pos.x, '*')
                
        # bottom wall
        if camera.is_visible(self.bottom_wall_right.pos):
            screen_pos = state.camera.to_screen_space(self.bottom_wall_right.pos)
            for i in range(camera.width - 2):
                if (1 + i < screen_pos.x and screen_pos.y < self.window_max_y - 1):
                    state.window.addch(screen_pos.y, 1 + i, '*')
        elif camera.is_visible(self.bottom_wall_left.pos):
            screen_pos = state.camera.to_screen_space(self.bottom_wall_left.pos)
            for i in range(camera.width - 2):
                if (screen_pos.x + i < (camera.width - 2) and screen_pos.y < self.window_max_y - 1):
                    state.window.addch(screen_pos.y, screen_pos.x + i, '*')
        elif camera.is_visible(self.bottom_wall_middle.pos):
            screen_pos = state.camera.to_screen_space(self.bottom_wall_middle.pos)
            for i in range(camera.width - 2):
                if (screen_pos.y < self.window_max_y - 1):
                    state.window.addch(screen_pos.y, 1 + i, '*')
        elif camera.is_visible(self.bottom_wall_middle_right.pos):
            screen_pos = state.camera.to_screen_space(self.bottom_wall_middle_right.pos)
            for i in range(camera.width - 2):
                if (screen_pos.y < self.window_max_y - 1):
                    state.window.addch(screen_pos.y, 1 + i, '*')
        elif camera.is_visible(self.bottom_wall_middle_left.pos):
            screen_pos = state.camera.to_screen_space(self.bottom_wall_middle_left.pos)
            for i in range(camera.width - 2):
                if (screen_pos.y < self.window_max_y - 1):
                    state.window.addch(screen_pos.y, 1 + i, '*')
        
        # top wall
        if camera.is_visible(self.top_wall_right.pos):
            screen_pos = state.camera.to_screen_space(self.top_wall_right.pos)
            for i in range(camera.width - 2):
                if (1 + i < screen_pos.x and screen_pos.y > 0):
                    state.window.addch(screen_pos.y, 1 + i, '*')
        elif camera.is_visible(self.top_wall_left.pos):
            screen_pos = state.camera.to_screen_space(self.top_wall_left.pos)
            for i in range(camera.width - 2):
                if (screen_pos.x + i < (camera.width - 2) and screen_pos.y > 0):
                    state.window.addch(screen_pos.y, screen_pos.x + i, '*')
        elif camera.is_visible(self.top_wall_middle.pos):
            screen_pos = state.camera.to_screen_space(self.top_wall_middle.pos)
            for i in range(camera.width - 2):
                if (screen_pos.y > 0):
                    state.window.addch(screen_pos.y, 1 + i, '*')
        elif camera.is_visible(self.top_wall_middle_right.pos):
            screen_pos = state.camera.to_screen_space(self.top_wall_middle_right.pos)
            for i in range(camera.width - 2):
                if (screen_pos.y > 0):
                    state.window.addch(screen_pos.y, 1 + i, '*')
        elif camera.is_visible(self.top_wall_middle_left.pos):
            screen_pos = state.camera.to_screen_space(self.top_wall_middle_left.pos)
            for i in range(camera.width - 2):
                if (screen_pos.y > 0):
                    state.window.addch(screen_pos.y, 1 + i, '*')
                    
        else:
            return


# keeps track of the current 'camera' position over the 2d world in world space
class Camera:
    def __init__(self, start_x, start_y, width, height):

        # indicates how large our 'view port' is
        self.width = width 
        self.height = height

        self.start_x = start_x
        self.start_y = start_y

        self.x = start_x
        self.y = start_y

    def is_visible(self, world_pos):
        # rectangle in screen_space around camera first
        rect = get_rect_from_center(self.x, self.y, self.width, self.height)

        # determine if the world_pos is in that rectangle
        return point_in_rect(rect[0][0], rect[0][1], rect[1][0], rect[1][1], world_pos.x, world_pos.y)
        
    def to_screen_space(self, world_pos):

        offSet_x = self.x - world_pos.x
        offSet_y = self.y - world_pos.y

        half_x = int(self.width / 2)
        half_y = int(self.height / 2)

        return ScreenPos(half_x - offSet_x, half_y - offSet_y)

class GameCommands:
    # TODO - Should these be something else besides numerals?
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    SHOOT = 5
    TOGGLE_DEBUG_INFO = 6
    QUIT = 7
    CAMERA_RIGHT = 8
    CAMERA_LEFT = 9
    CAMERA_UP = 10
    CAMERA_DOWN = 11

    def __init__(self): pass

    def on_up(self, state):
        player = state.world.player
        camera = state.camera
        monsters = state.world.monsters
        trees = state.world.trees
        common = state.world.common_tools

        if (player.y > (-state.world_y_compare_window)):
            for i in range(len(trees)):
                if (not common.object_clash(trees[i], player.x, (player.y - 1))):
                    return
            camera.y -= 1
            player.y -= 1
        
        for i in range(len(monsters)):
            if (camera.is_visible(monsters[i]) and (monsters[i].x == player.x)):
                if (monsters[i].y > player.y):
                    for j in range(len(trees)):
                        if (trees[j].y == monsters[i].y - 1 and trees[j].x == monsters[i].x):
                            return
                    monsters[i].y -= 1
                else:
                    for k in range(len(trees)):
                        if (trees[k].y == monsters[i].y + 1 and trees[k].x == monsters[i].x):
                            return
                    monsters[i].y += 1

    def on_left(self, state):
        player = state.world.player
        camera = state.camera
        monsters = state.world.monsters
        trees = state.world.trees
        common = state.world.common_tools

        if (player.x > (-state.world_x_compare_window)):
            for i in range(len(trees)):
                if (not common.object_clash(trees[i], (player.x - 1), player.y)):
                    return
            camera.x -= 1
            player.x -= 1
        
        for i in range(len(monsters)):
            if (camera.is_visible(monsters[i]) and (monsters[i].y == player.y)):
                if (monsters[i].x > player.x):
                    for j in range(len(trees)):
                        if (trees[j].x == monsters[i].x - 1 and trees[j].y == monsters[i].y):
                            return
                    monsters[i].x -= 1
                else:
                    for k in range(len(trees)):
                        if (trees[k].x == monsters[i].x + 1 and trees[k].y == monsters[i].y):
                            return
                    monsters[i].x += 1

    def on_down(self, state):
        camera = state.camera
        player = state.world.player
        monsters = state.world.monsters
        trees = state.world.trees
        common = state.world.common_tools

        if (player.y < (state.world_max_y - state.world_y_compare_window)):
            for i in range(len(trees)):
                if (not common.object_clash(trees[i], player.x, (player.y + 1))):
                    return
            camera.y += 1
            player.y += 1
        
        for i in range(len(monsters)):
            if (camera.is_visible(monsters[i]) and (monsters[i].x == player.x)):
                if (monsters[i].y > player.y):
                    for j in range(len(trees)):
                        if (trees[j].y == monsters[i].y - 1 and trees[j].x == monsters[i].x):
                            return
                    monsters[i].y -= 1
                else:
                    for k in range(len(trees)):
                        if (trees[k].y == monsters[i].y + 1 and trees[k].x == monsters[i].x):
                            return
                    monsters[i].y += 1

    def on_right(self, state):
        camera = state.camera
        player = state.world.player
        monsters = state.world.monsters
        trees = state.world.trees
        common = state.world.common_tools

        if (player.x < (state.world_max_x - state.world_x_compare_window)):
            for i in range(len(trees)):
                if (not common.object_clash(trees[i], (player.x + 1), player.y)):
                    return
            camera.x += 1
            player.x += 1

        for i in range(len(monsters)):
            if (camera.is_visible(monsters[i]) and (monsters[i].y == player.y)):
                if (monsters[i].x > player.x):
                    for j in range(len(trees)):
                        if (trees[j].x == monsters[i].x - 1 and trees[j].y == monsters[i].y):
                            return
                    monsters[i].x -= 1
                else:
                    for k in range(len(trees)):
                        if (trees[k].x == monsters[i].x + 1 and trees[k].y == monsters[i].y):
                            return
                    monsters[i].x += 1

    def on_shoot(self, state):
        world = state.world
        player = state.world.player

        world.bullet = Bullet(player.x, player.y)

    def toggle_debug_info(self, state):
        state.debug_info.show = not state.debug_info.show

    def quit(self, state):
        state.quit = True

    def camera_right(self, state):
        state.camera.x += 1

    def camera_left(self, state):
        state.camera.x -= 1

    def camera_up(self, state):
        state.camera.y -= 1
    
    def camera_down(self, state):
        state.camera.y += 1

# keeps track of variables that change frequently due to user choice, like user coordinate and etc.
class GameState:
    def __init__(self, window_max_y, window_max_x, world_max_y, world_max_x):
        self.quit = False
        self.start = 0
        
        default_start_x = int(window_max_x / 2)
        default_start_y = int(window_max_y / 2)

        self.window_max_x = window_max_x
        self.window_max_y = window_max_y

        self.world_max_x = world_max_x
        self.world_max_y = world_max_y
        self.world_x_compare_window = (world_max_x - window_max_x)/2
        self.world_y_compare_window = (world_max_y - window_max_y)/2
        self.world = World(default_start_x, default_start_y, world_max_x, world_max_y, self.world_x_compare_window, self.world_y_compare_window, window_max_x, window_max_y)

        self.window = None
        self.stats = Statistics()
        self.renderer = Renderer()
        self.camera = Camera(int(window_max_x / 2), int(window_max_y / 2), window_max_x, window_max_y)
        self.debug_info = DebugInfo()
        self.game_commands = GameCommands()
        

        self.commands = {
            ord('w') : GameCommands.UP,
            ord('a') : GameCommands.LEFT,
            ord('s') : GameCommands.DOWN,
            ord('d') : GameCommands.RIGHT,
            ord(' ') : GameCommands.SHOOT,
            ord('m') : GameCommands.TOGGLE_DEBUG_INFO,
            ord('q') : GameCommands.QUIT,
            ord('k') : GameCommands.CAMERA_RIGHT,
            ord('h') : GameCommands.CAMERA_LEFT,
            ord('u') : GameCommands.CAMERA_UP,
            ord('j') : GameCommands.CAMERA_DOWN,
        }

        self.command_handlers = {
            GameCommands.UP : self.game_commands.on_up,
            GameCommands.LEFT : self.game_commands.on_left,
            GameCommands.DOWN : self.game_commands.on_down,
            GameCommands.RIGHT : self.game_commands.on_right,
            GameCommands.SHOOT : self.game_commands.on_shoot,
            GameCommands.TOGGLE_DEBUG_INFO : self.game_commands.toggle_debug_info,
            GameCommands.QUIT : self.game_commands.quit,
            GameCommands.CAMERA_RIGHT : self.game_commands.camera_right,
            GameCommands.CAMERA_LEFT : self.game_commands.camera_left,
            GameCommands.CAMERA_UP : self.game_commands.camera_up,
            GameCommands.CAMERA_DOWN: self.game_commands.camera_down,
        }

        self.pending_commands = list()

    def run(self):
        while not self.quit:
            player = self.world.player
            monsters = self.world.monsters

            for i in range(len(monsters)):
                if (monsters[i].x == player.x and monsters[i].y == player.y):
                    curses.flash()
                    self.stats.lives_state(self, self.renderer, i)

            self.read_input()
            self.process_game_moves()
            self.run_bullet_manager()

            self.renderer.render(self)

    def read_input(self):
        c = self.window.getch()

        command_id = self.commands.get(c)
        if not command_id:
            return # error handling later! (this key was invalid)
        
        self.pending_commands.append(command_id)
        

    def process_game_moves(self):
        for command_id in self.pending_commands:
            command_handler = self.command_handlers.get(command_id)
            if not command_handler:
                continue # error handling later! (this command SHOUlD have been there!)
            command_handler(self)
        self.pending_commands.clear()


    def run_bullet_manager(self):
        if not self.world.bullet:
            return
        
        self.world.bullet.simulate(self)

        if self.world.bullet.shots_remaining < 0:
            self.world.bullet = None

class DebugInfo():
    def __init__(self):
        self.show = False
    
    def _render(self, state): 
        player = state.world.player

        if self.show:
            state.window.addstr(0, 17, f"wpos:{player.y}, {player.x}")

# stats of the user in the game
class Statistics:
    def __init__(self):
        self.score = 0
        self.health = 3

    def incr_score(self):
        self.score += 1

    def decr_health(self):
        self.health -= 1

    def lives_state(self, state, renderer, monsterNo):
        window = state.window
        monsters = state.world.monsters
        common = state.world.common_tools
        self.decr_health()

        if (self.health != 0):
            common.random_area_on_map(monsters[monsterNo], state)

        renderer.render(state)

        if (self.health == 0):
            renderer.render(state)
            window.addstr(2, 10, f"YOU LOSE!")
            window.refresh()
            time.sleep(1.5)
            exit()

    def _render(self, state):
        window = state.window
        window.addstr(0, 9, f"Score:{self.score}")
        window.addstr(0, 1, f"Lives:{self.health}")
        window.addstr(state.window_max_y - 1, 1, "Monster may dodge bullet!")
        

# TODO problem is that the bullet is skipping spaces I believe because we have multiple monsters now taking more time up 
# up before we get to the .5 frame if statement check
# bullet operations of the user
class Bullet(WorldObject):
    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y)
        self.x_count = 1
        self.shots_remaining = 3
        self.last_sim_time = time.time()
        self.frame_count = .1
    
    def _render(self, state):
        camera = state.camera
        if camera.is_visible(self.pos):
            screen_pos = state.camera.to_screen_space(self.pos)
            state.window.addch(screen_pos.y, screen_pos.x, 'a')
        else:
            return

    def simulate(self, state):
        world = state.world
        stats = state.stats
        monsters = state.world.monsters
        common = state.world.common_tools

        now = time.time()
        if (now - self.last_sim_time) <= .5:
            return
 
        temp_x = (self.start_x + self.x_count)

        if ((temp_x) < (world.max_x - 1)):
            self.x = temp_x 
            for i in range(len(monsters)):
                if (monsters[i].y == self.y and monsters[i].x == self.x):
                    common.random_area_on_map(monsters[i], state)
                    curses.flash()
                    stats.incr_score()
                self.x_count += 1

        self.shots_remaining -= 1
        self.last_sim_time = now

class Monster(WorldObject):
    def __init__(self):
        # TODO - we need to either pass this in or do something different so 
        # it's not static.
        super().__init__(3, 3)

    # renders the monster on the screen
    def _render(self, state):
        common = state.world.common_tools

        common.render_object(self, state, 'T')

class Tree(WorldObject):
    def __init__(self):
        super().__init__(3,4)

    def _render(self, state):
        common = state.world.common_tools

        common.render_object(self, state, '@')


# TODO: probably want to later put all these in a class to consolidate main functions
class CommonTools:
    def __init__(self):
        pass

    def object_clash(self, currObject, otherObject_x, otherObject_y):
        if(currObject.x == otherObject_x and currObject.y == otherObject_y):
            return False
        return True
        

    def render_object(self, object, state, char):
        camera = state.camera
        if camera.is_visible(object.pos):
            screen_pos = state.camera.to_screen_space(object.pos)
            state.window.addch(screen_pos.y, screen_pos.x, char)
        else:
            return

    def random_area_on_map(self, object, state):
        world = state.world
        player = state.world.player
        camera = state.camera

        x_boundary = world.world_x_compare_window + camera.width
        y_boundary = world.world_y_compare_window + camera.height

        object.y = random.randint(-world.world_y_compare_window, y_boundary)
        object.x = random.randint(-world.world_x_compare_window, x_boundary)

        if (object.y == player.y):
            object.y = random.randint(-world.world_y_compare_window, y_boundary)
            while (object.y == player.y):
                object.y = random.randint(-world.world_y_compare_window, y_boundary)
        elif (object.x == player.x):
            object.x = random.randint(-world.world_x_compare_window, x_boundary)
            while (object.x == player.x):
                object.x = random.randint(-world.world_x_compare_window, x_boundary)

def main():
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    window_width = 40
    window_height = 10
    world_width = 80
    world_height = 12

    game_state = GameState(window_height, window_width, world_height, world_width)
    game_state.window = curses.newwin(window_height, window_width)
    game_state.window.nodelay(True)

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