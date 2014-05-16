import textwrap
from config import *
import libtcodpy as libtcod
import random

# palette
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

#create the list of game messages and their colors, starts empty
game_msgs = []
game_state = 'playing'

#start game time at 0
ticks = 0

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
        if key.vk == libtcod.KEY_UP:
            return 'up'
        elif key.vk == libtcod.KEY_DOWN:
            return 'down'

        elif key.vk == libtcod.KEY_LEFT:
            window.activate_pane("-")

        elif key.vk == libtcod.KEY_RIGHT:
            window.activate_pane("+")

        elif key.vk == libtcod.KEY_SPACE:
            game_state = 'paused'
            message('Game Paused', libtcod.purple)

        else:
            return 'no action'
    elif game_state == 'paused':
        if key.vk == libtcod.KEY_SPACE:
            game_state = 'playing'
            message('Game Unpaused', libtcod.purple)


################################################################################
#Output
################################################################################

class Panel(object):
    """Class for all main GUI panels"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self._console = libtcod.console_new(self.width, self.height)
        libtcod.console_set_default_background(self._console, libtcod.black)

    def blit(self):
        libtcod.console_blit(self._console, 0, 0, self.width, self.height, 0, self.x, self.y)

    def _render_elements(self):
        pass

    def render(self):
        #prepare to render the panel
        self.blit()


class Gui(Panel):
    def __init__(self):
        super(Gui, self).__init__(0, SCREEN_HEIGHT - GUI_HEIGHT, SCREEN_WIDTH, GUI_HEIGHT)

    def render(self):
        libtcod.console_set_default_background(self._console, libtcod.black)
        libtcod.console_clear(self._console)
        #draw labels
        libtcod.console_set_default_foreground(self._console, libtcod.light_gray)
        libtcod.console_print_ex(self._console, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_control_under_mouse())

        #show the player's stats and messages
        render_bar(self._console, 1, 1, BAR_WIDTH, 'Popularity', 50, 100,
                   libtcod.light_blue, libtcod.darker_blue)
        self.render_messages()

        super(Gui, self).render()

    def render_messages(self):
        #print the game messages, one line at a time
        y = 1
        for (line, color) in game_msgs:
            libtcod.console_set_default_foreground(self._console, color)
            libtcod.console_print_ex(self._console, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1


class Pane(Panel):
    def __init__(self, pane_index, title, active=False):
        self.pane_index = pane_index
        self.title = title
        self.active = active
        super(Pane, self).__init__(pane_index * (SCREEN_WIDTH // PANE_NUMBER), 0, SCREEN_WIDTH // PANE_NUMBER,
                                   SCREEN_HEIGHT - GUI_HEIGHT)
        self._render_frame()

    def render(self):
        super(Pane, self).render()

    def _render_frame(self):
        """Renders the initial frame and title"""
        if self.active:
            libtcod.console_set_default_foreground(self._console, libtcod.dark_blue)
        else:
            libtcod.console_set_default_foreground(self._console, libtcod.darker_blue)

        libtcod.console_print_frame(self._console, 0, 0, self.width, self.height, False)
        libtcod.console_set_default_foreground(self._console, libtcod.light_gray)
        libtcod.console_print_ex(self._console, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, self.title)

    def activate(self):
        self.active = True
        self._render_frame()

    def deactivate(self):
        self.active = False
        self._render_frame()


class Window(object):
    def __init__(self):
        #initialise window
        libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Alien Democracy', False)

        #create main buffer
        self.buff = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        libtcod.console_set_default_foreground(self.buff, libtcod.white)
        libtcod.sys_set_fps(LIMIT_FPS)

        #create GUI
        self.gui = Gui()

        # create panels on left
        self.panes = []
        for i in range(PANE_NUMBER):
            self.panes.append(Pane(i, "Menu " + str(i + 1)))

        self.active_pane = 0
        self.panes[self.active_pane].activate()

    def render(self):
        # render panes and gui
        for pane in self.panes:
            pane.render()

        self.gui.render()

        #flush console
        libtcod.console_flush()

    def activate_pane(self, pane_id):
        if pane_id == '+':
            pane_id = min(self.active_pane + 1, PANE_NUMBER - 1)
        elif pane_id == '-':
            pane_id = max(self.active_pane - 1, 0)

        self.panes[self.active_pane].deactivate()
        self.active_pane = pane_id
        self.panes[self.active_pane].activate()


def render_bar(pane, x, y, total_width, name, value, maximum, bar_color, back_colour):
    #calculate width of bar
    bar_width = int(float(value) / maximum * total_width)

    #render background
    libtcod.console_set_default_background(pane, back_colour)
    libtcod.console_rect(pane, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #render bar
    libtcod.console_set_default_background(pane, bar_color)
    if bar_width > 0:
        libtcod.console_rect(pane, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #value
    libtcod.console_set_default_foreground(pane, libtcod.white)
    libtcod.console_print_ex(pane, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
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


def clear_all():
    pass


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
        self.population = random.randint(INITIAL_POP_MIN, INITIAL_POP_MAX)
        self.world_name = 'Zog'
        #TODO add init

    def simulate(self):
        #TODO: Add simulation of time passing

        self.population += random.randint(1, 10000)
        if self.population < 0:
            self.population = 0
        return False

    def status_report(self):
        return self.world_name + " now has " + str(self.population) + " citizens"

################################################################################
#Main program
################################################################################


# Initialise screen and buffers

populous = Populous()

# Initialise game variables

#welcome the player
message('Welcome!', libtcod.red)

window = Window()

# Main game loop

while not libtcod.console_is_window_closed():

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

    # Render console
    window.render()

    # Flush console

    # Clear objects from buffer
    clear_all()

    #handle keys and exit game if needed

    player_action = handle_input()

    if player_action == 'exit':
        break

    # if game is in play, then compute turn:
    if game_state == 'playing':
        if ticks % DAY_LENGTH == 0:
            populous.simulate()
            message("A new day begins", libtcod.white)
            message(populous.status_report(), libtcod.orange)

        ticks += 1
