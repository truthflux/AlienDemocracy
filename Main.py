import textwrap
from config import *

# palette

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)


################################################################################
#Input
################################################################################

mouse = libtcod.Mouse()
key = libtcod.Key()
game_state = 'playing'
player_action = None


def get_objects_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)
    names = [ob.name for ob in objects
             if ob.x == x and ob.y == y]
    names = ', '.join(names)  # join the names, separated by commas
    return names.capitalize()


def handle_input():
    global key, fov_recompute

    if key.vk == libtcod.KEY_ENTER and key.lalt:

        #Alt+Enter: toggle full screen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  # exit game

    if game_state == 'playing':
        # respond to movement keys
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player.move(0, -1)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player.move(0, 1)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player.move(-1, 0)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player.move(1, 0)
            fov_recompute = True

        else:
            return 'no action'

################################################################################
#Output
################################################################################

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)


def initialise_io():
    global panel, buff, fov_recompute

    libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Alien Democracy', False)
    panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
    libtcod.sys_set_fps(LIMIT_FPS)
    buff = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    libtcod.console_set_default_foreground(buff, libtcod.white)

    fov_recompute = True


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_colour):
    #calculate width of bar
    bar_width = int(float(value) / maximum * total_width)

    #render background
    libtcod.console_set_default_background(panel, back_colour)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #render bar
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #value
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def message(new_msg, color=libtcod.white):
    #split the message if necessary, among multiple lines

    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and the color
        game_msgs.append((line, color))


def render_messages():
    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1


def clear_all():
    for ob in objects:
        ob.clear()


def draw_all():
    global fov_recompute
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground

    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #draw map
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = level_map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if level_map[x][y].explored:
                        #it is out of the player's FOV
                        if wall:
                            libtcod.console_set_char_background(buff, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(buff, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    # it's visible
                    level_map[x][y].explored = True
                    if wall:
                        libtcod.console_set_char_background(buff, x, y, color_light_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(buff, x, y, color_light_ground, libtcod.BKGND_SET)

        #drw objects
        for ob in objects:
            ob.draw()

        libtcod.console_blit(buff, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

        fov_recompute = False

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #draw labels
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_objects_under_mouse())

    #show the player's stats and messages
    render_bar(1, 1, BAR_WIDTH, 'HP', 50, 100,
               libtcod.light_red, libtcod.darker_red)

    render_messages()

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


################################################################################
#Maps
################################################################################


class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return center_x, center_y

    def intersect(self, other):
        #returns true if this rectangle intersects with the other
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


def make_level():
    global level_map, fov_map

    #fill map with "blocked" tiles
    level_map = []
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            level_map.append(Tile(True))

    #create two rooms and a tunnel

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)

        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_room(new_room)
            place_objects(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y

            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #Create FOV map
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not level_map[x][y].block_sight, not level_map[x][y].blocked)


def create_room(room):
    global level_map
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            level_map[x][y].blocked = False
            level_map[x][y].block_sight = False


def place_objects(room):
    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):

        suitable = False
        while not suitable:
            #choose random spot for this monster
            x = libtcod.random_get_int(0, room.x1, room.x2)
            y = libtcod.random_get_int(0, room.y1, room.y2)

            if not is_blocked(x, y):
                suitable = True

        if libtcod.random_get_int(0, 0, 100) < 80:  # 80% chance of getting an orc
            #create an orc
            monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True)
        else:
            #create a troll
            monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True)

        objects.append(monster)


def create_h_tunnel(x1, x2, y):
    global level_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        level_map[x][y].blocked = False
        level_map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global level_map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        level_map[x][y].blocked = False
        level_map[x][y].block_sight = False


#TODO write universal tunnel creation function create_tunnel
################################################################################
#Government
################################################################################
class Government:
    def __init__(self):
        # Government creation process
        print "test"


################################################################################
#Populous
################################################################################

class Populous:
    def __init__(self):
        print("test")
        #TODO add init


################################################################################
#Game
################################################################################

def initialise_game():
    global player, objects
    player = Object(0, 0, '@', 'player', libtcod.white, blocks=True)
    objects = [player]
    make_level()


class Object:
    # this is a generic object: the player, a document, a car etc.
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks

    def move(self, dx, dy):
        #Check for blocked:
        if not is_blocked(self.x + dx, self.y + dy):
            #moves by the amount indicated
            self.x += dx
            self.y += dy

    def draw(self):
        #set the color and draws the character
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(buff, self.color)
            libtcod.console_put_char(buff, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erases from the buffer
        libtcod.console_put_char(buff, self.x, self.y, ' ', libtcod.BKGND_NONE)


def is_blocked(x, y):
    #test map tile
    if level_map[x][y].blocked:
        return True

    #check for blocking objects
    for ob in objects:
        if ob in objects:
            if ob.blocks and ob.x == x and ob.y == y:
                return True

    return False


################################################################################
#Beginning of main program
################################################################################


# Initialise screen and buffers
initialise_io()

# Initialise game variables
initialise_game()

#welcome the player
message('Welcome!', libtcod.red)

# Main game loop

while not libtcod.console_is_window_closed():

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

    # Render console
    draw_all()

    # Flush console
    libtcod.console_flush()

    # Clear objects from buffer
    clear_all()

    #handle keys and exit game if needed

    player_action = handle_input()
    if player_action == 'exit':
        break

    if game_state == 'playing' and player_action != 'no action':
        for obj in objects:
            if obj != player:
                message('The ' + obj.name + ' growls!', libtcod.orange)
