from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from go import Board, Game, IllegalMoveException, EMPTY, BLACK, WHITE
import cgi
import os
import random
import urlparse
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

env = Environment(
    loader=FileSystemLoader('./templates'),
    #autoescape=select_autoescape(['html', 'xml']),
    trim_blocks = True, undefined = StrictUndefined
)

index_html = env.get_template('index.html')

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

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # parse path out of the HTTP request
        parts = urlparse.urlparse(self.path)
        # (relative to root)
        path_components = parts.path[1:].split('/')

        # check for requests for static assets
        if len(path_components) == 2 and path_components[0] == 'assets':
            return self.do_GET_asset(path_components[1])

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        x = self.wfile.write

        x(index_html.render(METHOD = 'GET', GAME_STATE = game_state,
                          GREETING = self.greeting(),
                          RUNNING_BOARD = game_state.game.board.show_js(),
                          PROMPT = self.prompt()))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        if ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        if 'command' not in postvars:
            return self.error_bad_request()

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
            return self.error_bad_request()

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        x = self.wfile.write

        x(index_html.render(METHOD = 'POST', GAME_STATE = game_state,
                          GREETING = self.greeting(),
                          RUNNING_BOARD = game_state.game.board.show_js(),
                          PROMPT = self.prompt(),
                          RESULT_PRINT = self.result_print()))

    def error_bad_request(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        x = self.wfile.write
        x('Error: bad request')
        return

    def error_not_found(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        x = self.wfile.write
        x('Error: not found')
        return

    def show_board(self):
        return '<script>var board_js = ' + game_state.game.board.show_js() + '; updateBoard(board_js);</script>'

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
            return  '<br><br><h3>Hello! How about a nice game of Go?</h3><h4>' + \
                    game_state.game.whose_turn() + ' to play:</h4>'

        elif game_state.state == PLAYING:
            return '<br><br><h3>' + random.choice(playing_messages) + '</h3><h4>' + \
                   game_state.game.whose_turn() + ' to play:</h4>'

        elif game_state.state == SCORING:
            return "<br><br><h3>That was a tough game!</h3>"

        else:
            return "<br><br><h3>Thanks for the game!</h3>"

    def result_print(self):
        if game_state.removed == True:
            game_state.state = OVER
            black = game_state.game.score()[0][1]
            white = game_state.game.score()[1][1]
            game_state.removed = False
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
                return '<h4>Illegal move. Try again?</h4>'
            else:
                return '<h4>Play or Pass!</h4>'
        else:
            return ''

    def do_GET_asset(self, filename):
        # respond to a request for a static asset, e.g. image file
        rel_path = os.path.join('assets', filename)
        extension = filename.split('.')[-1]
        content_type = {'jpg': 'image/jpeg',
                        'png': 'image/png',
                        'css': 'text/css',
                        'js': 'text/javascript',
                        }.get(extension)

        try:
            data = open(rel_path, 'rb').read()
        except IOError:
            return self.error_not_found()

        self.send_response(200)
        if content_type:
            self.send_header('Content-type', content_type)
        self.send_header('Content-length', bytes(len(data)))
        # allow the browser to cache these assets for 30 seconds
        self.send_header('Cache-Control', 'public, max-age=30')
        self.end_headers()

        self.wfile.write(data)


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), MyHandler)
    server.serve_forever()
