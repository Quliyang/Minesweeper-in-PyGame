import itertools
import random

_SAFE = 0
_MINE = 1
_FLAGGED = 2
_OPEN = 4
_OPEN_MINE = _MINE | _OPEN


class MineSweeperBoard:

    def __init__(self, grid, mines, cols, lines):
        """
        Initialises `MineSweeperBoard` instances.

        :param grid: {dict<tuple<int>, int>} the grid of cells
        :param mines: {int} amount of mines
        :param cols: {int} width
        :param lines: {int} height
        """
        self.grid = grid
        self.mines_left = mines
        self.hints = {}
        self.cols = cols
        self.lines = lines
        self.last_clicked = None
        self.cells_revealed = 0
        self.safe_cells = cols * lines - mines

    @classmethod
    def random(cls, cols, lines, num_of_mines):
        """
        Creates a `MineSweeperBoard` instance with random mine placement.

        :param cols: {int} width
        :param lines: {int} height
        :param num_of_mines: {int} amount of mines to be placed
        :return: {MineSweeperBoard} randomized instance
        """
        cells = list(itertools.product(range(cols), range(lines)))
        mines = random.sample(cells, num_of_mines)
        grid = {pos: [_SAFE, _MINE][pos in mines] for pos in cells}
        return cls(grid, num_of_mines, cols, lines)

    def action(self, position, flag=False):
        """
        The click on a cell.

        :param position: {tuple<int>} position of clicked cell
        :param flag: {bool} cell shall be flagged/unflagged
        :return: {None}
        """
        state = self[position]
        if state == _OPEN:
            return
        if flag:
            self.flag(position, state)
        elif state & _FLAGGED == _FLAGGED:
            return
        else:
            self.reveal(position, state)

    def flag(self, position, state):
        """
        Flags/unflags a given cell.

        :param position: {tuple<int>} position of the cell
        :param state: {int} state of the cell
        :return: {None}
        """
        if state & _FLAGGED == _FLAGGED:
            self[position] ^= _FLAGGED
        else:
            self[position] |= _FLAGGED

        if state == _MINE:
            self.mines_left -= 1
        elif self[position] == _MINE:
            self.mines_left += 1

    def reveal(self, position, state):
        """
        Opens a cell and recursively opens it's neighbors if there are
        no mines next to it.

        :param position: {tuple<int>} position of the cell
        :param state: {int} state of the cell
        :return: {None}
        """
        self.last_clicked = state
        self[position] |= _OPEN
        if state == _MINE:
            return
        self.cells_revealed += 1
        neighbors = list(self.get_neighbors(position))
        mines_nearby = sum(self[pos] & _MINE == _MINE for pos in neighbors)
        self.hints[position] = mines_nearby
        if mines_nearby == 0:
            for neighbor in neighbors:
                self.action(neighbor)

    def get_neighbors(self, position):
        neighbors = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
        ]
        x, y = position
        for dy, dx in neighbors:
            x2 = x+dx
            y2 = y+dy
            if 0 <= x2 < self.cols and 0 <= y2 < self.lines:
                yield (x2, y2)

    def open_mines(self):
        for position, state in self:
            if state & _MINE == _MINE:
                self[position] = _OPEN_MINE

    def __iter__(self):
        return iter(self.grid.items())

    def __contains__(self, item):
        return item in self.grid

    def __getitem__(self, key):
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value

