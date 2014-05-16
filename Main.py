import textwrap
from config import *
import libtcodpy as libtcod

# palette
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

#create the list of game messages and their colors, starts empty
game_msgs = []
game_state = 'playing'

#start game time at 0
time = 0

################################################################################
#Input
################################################################################

mouse = libtcod.Mouse()
key = libtcod.Key()
player_action = None


def get_control_under_mouse():
    global mouse

    # #return a string with the names of all objects under the mouse
    # (x, y) = (mouse.cx, mouse.cy)
    # names = [ob.name for ob in objects
    #          if ob.x == x and ob.y == y]
    # names = ', '.join(names)  # join the names, separated by commas

    # Temporary fudge while debugging
    #TODO: Implement mouse look

    names = 'No Control'

    return names.capitalize()


def handle_input():
    global key, game_state

    if key.vk == libtcod.KEY_ENTER and key.lalt:

        #Alt+Enter: toggle full screen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  # exit game

    if game_state == 'playing':
        # respond to movement keys
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            return 'up'
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            return 'down'

        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            return 'left'

        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            return 'right'

        elif libtcod.console_is_key_pressed(libtcod.KEY_SPACE):
            game_state = 'paused'
            message('Game Paused')

        else:
            return 'no action'
    elif game_state == 'paused':
        if libtcod.console_is_key_pressed(libtcod.KEY_SPACE):
            game_state = 'playing'
            message('Game Unpaused')


################################################################################
#Output
################################################################################


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
    if DEBUG:
        print(new_msg)

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
    return False


def draw_all():

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #draw labels
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_control_under_mouse())

    #show the player's stats and messages
    render_bar(1, 1, BAR_WIDTH, 'Popularity', 50, 100,
               libtcod.light_blue, libtcod.darker_blue)

    render_messages()

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

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
        self.population = random.randint(INITIAL_POP_MIN,INITIAL_POP_MAX)
        world_name = 'Zog'
        message('%s has %s citizens') % (world_name, self.population)
        #TODO add init

    def simulate(self):

        #TODO: Add simulation of time passing
        return False

################################################################################
#Beginning of main program
################################################################################


# Initialise screen and buffers
initialise_io()

# Initialise game variables

#welcome the player
message('Welcome!', libtcod.red)

# Main game loop

populous = new Populous

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
        time += 1
        Populous.simulate