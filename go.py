# Rules of go implementation
# Lines on the go board are numbered starting from 0 (e.g. 0-18 on a 19x19 board)
# Coordinates should be represented as (x,y) tuples
# Last move format: [COLOR, coord] or [COLOR, 'PASS']

import copy
from collections import deque

EMPTY = '+'
BLACK = '@'
WHITE = 'O'

CHINESE = 'C'
JAPANESE = 'J'

class IllegalMoveException(Exception):
    pass

class Game(object):

    def __init__(self, size, data=None, rule_set=JAPANESE):
        self.size = size
        self.rule_set = rule_set
        self.board = Board(size)
        self.is_finished = False

    # Returns the color of the current turn
    def whose_turn(self):
        if self.board.last_move == None or self.board.last_move[0] == WHITE:
            return 'BLACK'
        else:
            return 'WHITE'

    # Receives user input as a string and remove the dead stones
    def remove_dead_stones(self, stone_string): # once coords come as ' 6,5  12,7 9,6 '
        coords = stone_string.strip().split()
        remove = [tuple(map(int, x.split(','))) for x in coords]
        for x in remove:
            if self.board.which_color(x) == WHITE:
                self.board.blacks_prisoners += 1
            elif self.board.which_color(x) == BLACK:
                self.board.whites_prisoners += 1
        self.board.remove_stones(remove)

    # Caluculates the scores and return the results in a list
    def score(self):
        blacks_points = self.board.blacks_prisoners
        whites_points = self.board.whites_prisoners
        if self.rule_set == JAPANESE:
            whites_points += 6.5

        elif self.rule_set == CHINESE:
            whites_points += 7.5

        score_board = copy.deepcopy(self.board.board)
        empty = self.get_empty()
        while len(empty) > 0:
            for x in list(empty):
                check = self.board.adjacent_coords(x)
                color = set()
                for i in check:
                    color.add(score_board[i[0]][i[1]])

                if BLACK in color and WHITE not in color:
                    blacks_points += 1
                    score_board[x[0]][x[1]] = BLACK
                    empty.remove(x)

                elif WHITE in color and BLACK not in color:
                    whites_points += 1
                    score_board[x[0]][x[1]] = WHITE
                    empty.remove(x)

                elif BLACK in color and WHITE in color:
                    empty.remove(x)

        return [['BLACK', blacks_points], ['WHITE', whites_points]]

    # This function is to help scoring.
    def get_empty(self):
        spaces = set()
        i = 0
        while i < self.size:
            j = 0
            while j < self.size:
                if self.board.board[i][j] == EMPTY:
                    spaces.add((i, j))
                j += 1
            i += 1
        return spaces

class Board(object):
    def __init__(self, size, data=None):
        # store board position as a list of lists
        #self.board = []
        self.size = size
        if data is None:
            self.board = [([EMPTY] * size) for i in range(0, size)]
        else:
            lines = data.strip().split()
            self.board = [list(line) for line in lines]
            assert len(self.board) == size
            for line in self.board:
                assert len(line) == size
        self.last_move = None
        self.whites_prisoners = 0
        self.blacks_prisoners = 0
        self.previous_positions = deque([], 8)

    # For copying board positions
    def copy(self):
        ret = Board(self.size)
        ret.board = copy.deepcopy(self.board)
        ret.last_move = self.last_move
        ret.whites_prisoners = self.whites_prisoners
        ret.blacks_prisoners = self.blacks_prisoners
        # note: previous_positions is NOT copied over
        return ret

    # For print function
    def __repr__(self):
        return 'Board(%d, %r)' % (self.size, self.show())

    def show(self):
        # returns a string like "++++++@@@@@+++\n+++++++++++\n++++...."
        return '\n'.join(''.join(x) for x in self.board)

    def show_js(self):
        return str([''.join(x) for x in self.board])

    # Play a move at coord and remove any captured stones
    def add_move(self, color, coord, ignore_repeat = False):

        # Is the position suicide? Does it capture?
        if self.is_suicide(color, coord) and len(self.is_capturing(color, coord)) == 0:
            raise IllegalMoveException()

        # No board repetition / Ko
        if not ignore_repeat and self.is_repeat(color, coord):
            raise IllegalMoveException()

        # Is the position empty?
        if self.which_color(coord) != EMPTY:
            raise IllegalMoveException()

        # Remove the captured stones
        remove = list(self.is_capturing(color, coord))
        if len(remove) >= 1:
            self.remove_stones(remove)
            if color == BLACK:
                self.blacks_prisoners += len(remove)
            else:
                self.whites_prisoners += len(remove)

        # Update board, last move, previous_positions
        row, col = coord
        self.board[row][col] = color
        self.last_move = [color, coord]
        self.previous_positions.append(copy.deepcopy(self.board))

    # Returns a set of coordinates for captured groups
    def is_capturing(self, color, coord):
       adj = self.adjacent_coords(coord)
       captured = set()
       for x in adj:
           if self.which_color(x) not in (color, EMPTY):
               libs = self.liberty_count(x)
               if libs == 1:
                   capture = self.connected_stones(x)
                   if capture not in captured:
                       captured |= capture
       return captured

    # Internal tool for checking things
    def _add_move(self, color, coord):
        row, col = coord
        self.board[row][col] = color

    def add_pass(self):
        if self.last_move == None or self.last_move[0] == WHITE:
            self.last_move = [BLACK, 'PASS']
        else:
            self.last_move = [WHITE, 'PASS']
        self.previous_positions.append(['PASS'])

    def remove_stones(self, remove_list):
        for x in remove_list:
            self.board[x[0]][x[1]] = EMPTY

    # No index error please
    def in_bounds(self, coord):
        x, y = coord
        return (x >= 0 and x < self.size and
                y >= 0 and y < self.size)

    # Return list of all coordinates adjacent to "coord" that are on the board
    def adjacent_coords(self, coord):
        x, y = coord
        coords = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        coords = filter(self.in_bounds, coords)
        return coords

    def which_color(self, coord):
        return self.board[coord[0]][coord[1]]

    # Return list of stones in the group containing "coord", including the stone
    # at "coord" itself
    def connected_stones(self, coord, seen = None):
        if seen is None:
            seen = set()
        elif coord in seen:
            return set()

        seen.add(coord)
        check_space = self.adjacent_coords(coord)
        color = self.which_color(coord)
        group = set([coord])
        for x in check_space:
            if self.which_color(x) == color:
                group.add(x)
                group |= self.connected_stones(x, seen)
        return group

    # Return the number of liberties on the group that contains "coord"
    def liberty_count(self, coord):
        group = self.connected_stones(coord)
        counted = set()
        for x in group:
            count_space = self.adjacent_coords(x)
            for y in count_space:
                if self.which_color(y) == EMPTY:
                    #if y not in counted:
                    counted.add(y)
        return len(counted)

    # Return True if the move on coord is a suicide
    def is_suicide(self, color, coord):
        remembered_color = self.which_color(coord)

        self._add_move(color, coord)
        suicide = (self.liberty_count(coord) == 0)

        self._add_move(remembered_color, coord)
        return suicide

    # Return True if the board has been repeated in the last 8 moves
    def is_repeat(self, color, coord):
        temp_board = self.copy()
        temp_board.add_move(color, coord, ignore_repeat = True)

        return temp_board.board in self.previous_positions
