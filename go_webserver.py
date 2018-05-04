from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from go import Board, Game, IllegalMoveException, EMPTY, BLACK, WHITE
import cgi
import random

# To track the game state across requests, we use a "ServerState" object.
# In the future, this might be stored in a database.

# values for self.state:
WAITING = 'WAITING' # before the first move
PLAYING = 'PLAYING' # new moves are being played
SCORING = 'SCORING' # no more moves, players are marking dead groups now
OVER = 'OVER' # game is finished and scored

class ServerState(object):

    def __init__(self):
        self.game = Game(19)
        self.illegal = False
        self.removed = False
        self.state = WAITING

game_state = ServerState()

form_html_move = '<form method="post"> X coord: <input type="text" name="xcoord"><br> Y coord: <input type="text" name="ycoord"><br> <input type="hidden" name="command" value="New Move"> <input type="submit" name="button" value="Submit the move"></form>'

form_html_pass = '<form method="post"> <input type="hidden" name="command" value="Pass"> <input type="submit" name="button" value="Pass"></form>'

form_html_resign = '<form method="post"> <input type="hidden" name="command" value="Resign"> <input type="submit" name="button" value="Resign"></form>'

form_html_dead = '<form method="post"> Select dead stones: <input type="text" name="dead"><br> <input type="hidden" name="command" value="Dead Stones"><input type="submit" name="button" value="Submit"></form>'

form_html_new = '<form method="post"> <input type="hidden" name="command" value="New Game"> <input type="submit" name="button" value="New Game">'

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        x = self.wfile.write

        x(self.show_board())
        x(self.greeting())
        x(self.prompt())
        x(self.playing_tools())

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        if ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        if 'command' not in postvars:
            return self.error_handler()

        command = postvars['command'][0]

        if command == 'New Move':
            try:
                xcoord = int(postvars['xcoord'][0])
                ycoord = int(postvars['ycoord'][0])
                game_state.state = PLAYING
            except ValueError:
                game_state.illegal = True

            if not game_state.illegal:
                coord = (xcoord, ycoord)
                if not game_state.game.board.in_bounds(coord):
                    game_state.illegal = True

            if not game_state.illegal:
                if game_state.game.whose_turn() == 'BLACK':
                    color = BLACK
                else:
                    color = WHITE
                try:
                    game_state.game.board.add_move(color, coord)
                except IllegalMoveException:
                    game_state.illegal = True

        elif command == 'Pass':
            if game_state.game.board.last_move[1] == 'PASS':
                game_state.state = SCORING
            game_state.game.board.add_pass()

        elif command == 'New Game':
            game_state.game = Game(19)
            game_state.state = WAITING

        elif command == 'Resign':
            game_state.state = OVER

        elif command == 'Dead Stones':
            if postvars['dead'][0] != '':
                game_state.game.remove_dead_stones(postvars['dead'][0])
            game_state.removed = True

        else:
            return self.error_handler()

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        x = self.wfile.write

        x(self.show_board())
        x(self.greeting())
        x(self.remove_dead())
        x(self.result_print())
        x(self.prompt())
        x(self.playing_tools())

    def error_handler(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        x = self.wfile.write
        x('Error: bad request')
        return

    def show_board(self):
        return 'Welcome to Haylee Go' + \
               '<pre>' + game_state.game.board.show() + '</pre>'

    def greeting(self):
        playing_messages = [
        "Hmmm, that's an interesting move!",
        "Is that sente?",
        "I didn't see that one!",
        "That's a nice move!",
        "It's complicated...",
        "Who is winning??",
        "You are good!",
        "Are you an AGA member yet?",
        ]

        if game_state.state == WAITING:
            return  'Hello! How about a nice game of Go?<br><br>' + \
                    game_state.game.whose_turn() + ' to play:<br>'

        elif game_state.state == PLAYING:
            return random.choice(playing_messages) + '<br><br>' + \
                   game_state.game.whose_turn() + ' to play:<br>'

        elif game_state.state == SCORING:
            return "That was a tough game!<br><br>"

        else:
            return "Thanks for the game!<br><br>"


    def remove_dead(self):
        if game_state.state == SCORING and game_state.removed == False:
            return form_html_dead
        else:
            return ' '

    def result_print(self):
        if game_state.removed == True:
            game_state.state = OVER
            black = game_state.game.score()[0][1]
            white = game_state.game.score()[1][1]
            if black > white:
                diff = black - white
                return 'Final score: Black ' + str(black) + ' points, White ' + str(white) + ' points<br>Black won by ' + str(diff) + ' points.<br>'
            else:
                diff = white - black
                return 'Final score: Black ' + str(black) + ' points, White ' + str(white) + ' points<br>White won by ' + str(diff) + ' points.<br>'
        else:
            return ' '

    def prompt(self):
        if game_state.state in [PLAYING, WAITING]:
            if game_state.illegal:
                game_state.illegal = False
                return 'Illegal move. Try again?<br>'
            else:
                return 'Play or Pass!<br>'
        else:
            return ' '

    def playing_tools(self):
        if game_state.state in [PLAYING, WAITING]:
            return form_html_move + form_html_pass + form_html_resign + form_html_new
        else:
            return form_html_new


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), MyHandler)
    server.serve_forever()
