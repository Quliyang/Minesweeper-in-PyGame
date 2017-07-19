import sys
from functools import wraps

import pygame as pg

import minesweeper as ms
from minesweeper import _SAFE, _MINE, _FLAGGED, _OPEN, _OPEN_MINE
from vectors import Vector


_LCLICK, _RCLICK = 1, 3

FPS = 30
BLOCK_SIZE = 40
FONT_SIZE = BLOCK_SIZE

HIDDEN_COLOR = (170, 170, 170)
FLAGGED_COLOR = (100, 100, 200)
OPEN_COLOR = (255, 255, 255)
MINE_COLOR = (255, 0, 0)
DEFAULT_TEXT_COLOR = BLACK = (0, 0, 0)
DEATH_MSG_COLOR = (110, 110, 110)

state_to_color = {
    _SAFE: HIDDEN_COLOR,
    _MINE: HIDDEN_COLOR,
    _FLAGGED: FLAGGED_COLOR,
    _FLAGGED | _MINE: FLAGGED_COLOR,
    _OPEN: OPEN_COLOR,
    _OPEN_MINE: MINE_COLOR
}

neighbor_mines_to_color = {
    1: (  0,  65, 170),  # blue
    2: ( 28, 122,   0),  # green
    3: (183,  25,  25),  # red
    4: (  3,  14,  76),  # blue
    5: ( 76,   3,   3),  # darkred
    6: (  6, 111, 124),  # cyan
    7: ( 10,  10,  10),  # black
    8: (171, 186, 188),  # grey
}


def require_state(state, bool_=True):
    """
    A decorator of second degree, that calls the decorated method only
    if the specified attribute of the object, that currently binds the
    method, has the same value as `_bool`.

    :param state: {str} attribute to be checked
    :param bool_: {bool} boolean value the attribute is checked against
    :return: {function} decorator
    """
    def dec(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if getattr(self, state) == bool_:
                method(self, *args, **kwargs)
        return wrapper
    return dec


def center_text(text, pos):
    """
    Takes text and it's position and calculates the position
    ii shoud have to be centered in it's tile.

    :param text: {pygame.Surface} text to be centered
    :param pos: {tuple<int>} non-centering position
    :return: {tuple<pygame.Surface, tuple<int, float>>} text and position
    to center it
    """
    text_rect = text.get_rect()
    x = pos[0] + text_rect.width // 2
    y = pos[1] + 1.5
    return text, (x, y)


class MineSweeperGame:

    def __init__(self, cols, lines, mines):
        """
        Initialises `MineSweeperGame` instances.

        :param cols: {int} width
        :param lines: {int} height
        :param mines: {int} amount of mines
        """
        pg.display.set_caption('MineSweep')
        self.cols = cols
        self.lines = lines
        self.mines = mines
        self.block_size = BLOCK_SIZE
        world_size = Vector((cols, lines))
        self.world = pg.display.set_mode(world_size * self.block_size)
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.font = pg.font.Font('freesansbold.ttf', FONT_SIZE)
        self.playing = False
        self.reset()

    @classmethod
    def from_mode(cls, mode):
        """
        User can choose one out of 3 predefined setups.

        :param mode: {str} difficulty selected by user
        :return: {MineSweeperGame} from predefined values
        """
        values = {
            'easy': (8, 8, 10),
            'medium': (16, 16, 40),
            'hard': (30, 16, 99)
        }[mode]
        return cls(*values)

    @classmethod
    def from_custom(cls):
        """
        Creates an instance with custom setup with some boundaries.

        :return: {MineSweeperGame} from custom setup
        """
        maximum_values = (30, 24, 667)
        try:
            user_values = cls.get_custom_input()
            if any(maxv < maxv - uv < 0
                   for maxv, uv
                   in zip(maximum_values, user_values)):
                raise ValueError()
        except ValueError:
            cls.alert_invalid_custom_input()
        else:
            return cls(*user_values)

    @staticmethod
    def get_custom_input():
        """
        Let's the user make his own setup.

        :return: {tuple<int>} values for width, height and mines
        """
        cols = int(input('Width (<31): '))
        lines = int(input('Height (<25): '))
        mines = int(input('Mines (<668): '))
        return cols, lines, mines

    @staticmethod
    def alert_invalid_custom_input():
        print('Ungültige Eingabe')

    @require_state('playing', False)
    def reset(self):
        """
        Resets game to beginning of a round.

        :return: {None}
        """
        self.playing = True
        self.won = False
        self.board = ms.MineSweeperBoard.random(self.cols, self.lines, self.mines)

    def game_loop(self):
        """
        Handles input and calls `self.update` and `self.draw`.

        :return: {None}
        """
        callbacks = {
            pg.MOUSEBUTTONDOWN: self.handle_mouse_input,
            pg.KEYDOWN: self.handle_key_input,
            pg.QUIT: sys.exit
        }
        while True:
            self.clock.tick(FPS)
            for e in pg.event.get():
                if e.type in callbacks:
                    callbacks[e.type](e)
            self.update()
            self.draw()

    @require_state('playing')
    def handle_mouse_input(self, e):
        """
        Starts an action for the cell the mouse is hovering according
        to the button that was pressed.

        :param e: {pygame.Event} mouse press event to process
        :return: {None}
        """
        pos = Vector(e.pos) // self.block_size
        if e.button == _LCLICK:
            self.board.action(pos)
        elif e.button == _RCLICK:
            self.board.action(pos, flag=True)

    def handle_key_input(self, e):
        """
        Acts in reaction to a key press.

        :param e: {pygame.Event} key press event to process
        :return: {None}
        """
        if e.key == pg.K_r:
            self.reset()

    def update(self):
        """
        Checks whether the game is over.

        :return: {None}
        """
        self.won = self.board.mines_left <= 0 or self.board.cells_revealed == self.board.safe_cells
        lost = self.board.last_clicked == _MINE
        if self.won or lost:
            self.playing = False
            self.board.last_clicked = None
            self.board.open_mines()

    def draw(self):
        """
        Draws the cells.

        :return: {None}
        """
        for cell, state in self.board:
            rect = Vector(cell) * self.block_size, (self.block_size, self.block_size)
            pg.draw.rect(self.screen, state_to_color[state], rect)
            if state == _OPEN:
                self.draw_hint(cell)
        if not self.playing:
            self.draw_game_over()
        self.draw_grid_lines()
        pg.display.update()

    def draw_grid_lines(self):
        """
        Draws the lines separating the cells.

        :return: {None}
        """
        for i in range(1, self.cols):
            start = i * self.block_size, 0
            end = i * self.block_size, self.lines * self.block_size
            pg.draw.line(self.screen, BLACK, start, end)
        for i in range(1, self.lines):
            start = 0, i * self.block_size
            end = self.cols * self.block_size, i * self.block_size
            pg.draw.line(self.screen, BLACK, start, end)

    def draw_hint(self, position):
        """
        Draws the digit that equals the amount of neighboring
        mines for a specific cell.

        :param position: {tuple<int>} position of cell
        :return: {None}
        """
        hint = self.board.hints[position]
        if hint == 0:
            return
        pos = Vector(position) * self.block_size
        color = neighbor_mines_to_color[hint]
        self.draw_text(str(hint), pos, color, center_text)

    def draw_text(self, text, pos, color=DEFAULT_TEXT_COLOR, *modifiers):
        """
        Writes text to an arbitrary position on the screen.

        :return: {None}
        """
        text = self.font.render(text, 1, color)
        for modifier in modifiers:
            text, pos = modifier(text, pos)
        self.screen.blit(text, pos)

    def draw_game_over(self):
        """
        Draws a message if the game has ended.

        :return: {None}
        """
        if self.won:
            msg = 'You won!'
        else:
            msg = 'You lost!'
        self.draw_text(f'{msg} Press [R] to restart', pos=(20, 5), color=DEATH_MSG_COLOR)
