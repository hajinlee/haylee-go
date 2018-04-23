from go import Board
from go import Game
from go import IllegalMoveException
import sys, getopt

EMPTY = '+'
BLACK = '@'
WHITE = 'O'


if __name__ == '__main__':
    board_size = 9
    opts, args = getopt.getopt(sys.argv[1:], "", ["19x19","13x13","9x9"])
    for key, val in opts:
        if key == '--19x19': board_size = 19
        elif key == '--13x13': board_size = 13
        elif key == '--9x9': board_size = 9

    in_filename = args[0] if len(args) >= 1 else '-'
    in_file = open(in_filename, 'r') if in_filename != '-' else sys.stdin

    game = Game(board_size)

    while not game.is_finished:
        print 'Submit your move or PASS:'
        coord = in_file.readline().strip()
        if not coord:
            break # done

        if in_file is not sys.stdin:
            print coord

        if coord.upper() == 'PASS':
            if game.board.last_move[1] == 'PASS':
                print 'Both player passed. The game is finished.'
                game.is_finished = True

            else:
                game.board.add_pass()
        else: # coord should come in like '12,13'
            coord = tuple(map(int, coord.split(',')))

            try:
                if game.board.last_move is None or game.board.last_move[0] == WHITE:
                    game.board.add_move(BLACK, coord)
                else:
                    game.board.add_move(WHITE, coord)
            except IllegalMoveException:
                print 'Illegal move, try again.'

            print game.board.show()
            print game.whose_turn(), 'TO PLAY'

    print 'End of moves, final board is:'
    print game.board.show()

    print 'Select dead stones:'
    coords = sys.stdin.readline().strip()
    if coords:
        game.remove_dead_stones(coords)

    print 'Scoring...'
    black = game.score()[0][1]
    white = game.score()[1][1]
    print 'Final score:', 'Black', black, 'points,', 'White', white, 'points'
    if black > white:
        print 'Black won by', black - white, 'points.'
    else:
        print 'White won by', white - black, 'points.'
