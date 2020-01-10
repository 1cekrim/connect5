import os
import string
import random
import numpy as np
import logging

from functools import wraps, reduce
from flask import Flask, request, current_app, session, escape, jsonify

ADMIN_PASSWORD = 'rla92233'
GRID_SIZE = 15
HOST = '127.0.0.1'
PORT = 12345
IS_DEBUG = False

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG if IS_DEBUG else logging.INFO)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

app.logger.removeHandler(app.logger.handlers[0])
app.logger.addHandler(stream_handler)


class Player:
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.valid_game = False
        self.game = None


class InvalidTurnException(Exception):
    pass


class InvalidActionException(Exception):
    pass


class Game:
    def __init__(self, config: dict):
        self.config = config
        self.column_size = self.config['size']
        self.row_size = self.config['size']
        self.black_player = self.config['black']
        self.white_player = self.config['white']
        self.game_name = self.config['name']
        self.current_player = self.black_player
        self.grid = np.zeros((self.column_size, self.row_size), dtype='int64')
        self.history = []

    def get_state(self, player_name: str):
        self._check_turn(player_name)

        state = {}
        state['grid'] = self.grid.tolist()
        state['color'] = 'black' if player_name == self.black_player.player_name else 'white'
        state['opponent_action'] = self.history[-1] if len(
            self.history) > 0 else None

        return state

    def serialize(self):
        state = {}
        state['column_size'] = self.column_size
        state['row_size'] = self.row_size
        state['black_player_name'] = self.black_player.player_name
        state['white_player_name'] = self.white_player.player_name
        state['game_name'] = self.game_name
        state['current_player_name'] = self.current_player.player_name
        state['grid'] = self.grid.tolist()

        return state

    def do_action(self, player_name: str, pos_y: int, pos_x: int):
        self._check_turn(player_name)
        self._check_pos(player_name, pos_y, pos_x)

        is_black = True if player_name == self.black_player.player_name else False

        self.grid[pos_y][pos_x] = 1 if is_black else 2

        self.history.append({'turns_since': len(self.history), 'player_name': player_name,
                             'color': 'black' if is_black else 'white', 'x': pos_x, 'y': pos_y})

        self.current_player = self.white_player if is_black else self.black_player

    def get_history(self):
        return self.history

    def _check_turn(self, player_name: str):
        if self.current_player.player_name != player_name:
            raise InvalidTurnException

    def _check_pos(self, player_name: str, pos_y: int, pos_x: int):
        if pos_y < 0 or pos_x < 0 or pos_y >= self.column_size or pos_x >= self.row_size or self.grid[pos_y][pos_x] != 0:
            raise InvalidActionException


def random_name(length, lst):
    strs = string.ascii_letters + string.digits
    while True:
        result = ""
        for _ in range(length):
            result += random.choice(strs)
        if not lst or result not in lst:
            return result


def only_when_change_logger(caller: str, message: str, state: int):
    if caller in session and session[caller] == state:
        return
    current_app.logger.info(f'{caller}: {message}')
    session[caller] = state


def check_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'player_name' in session:
            only_when_change_logger('check_login', 'Please login first.', 0)
            return 'Please login first.', 401
        if not session['player_name'] in current_app.players:
            only_when_change_logger('check_login', 'Session has expired.', 1)
            return 'Session has expired.', 401
        only_when_change_logger(
            'check_login',  f'{session["player_name"]} is logged in.', 2)
        return func(*args, **kwargs)
    return wrapper


def check_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'admin_password' in request.form:
            only_when_change_logger('check_admin', 'Bad Request.', 0)
            return 'Bad Request.', 400
        if request.form['admin_password'] != ADMIN_PASSWORD:
            only_when_change_logger('check_admin', 'Access denied.', 1)
            return 'Access denied.', 403
        only_when_change_logger('check_admin', 'Verified.', 2)
        return func(*args, **kwargs)
    return wrapper


def check_game_started(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        player = current_app.players[session['player_name']]
        if not player.valid_game:
            only_when_change_logger(
                'check_game_started', f'{session["player_name"]} is not included in any match.', 0)
            return 'Game did not start.', 409
        only_when_change_logger(
            'check_game_started', f'{player.player_name} is included in {player.game.game_name}', 1)
        return func(*args, **kwargs)
    return wrapper


def logger_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_app.logger.debug(f'{func.__name__} Start')
        result = func(*args, **kwargs)
        current_app.logger.debug(f'{func.__name__} End')
        return result
    return wrapper


@app.route('/login', methods=['POST'])
@logger_decorator
def login():
    if 'player_name' in session:
        player_name = escape(session["player_name"])
        current_app.logger.info(
            f'{player_name} failed to log in successfully.')
        return f'Please logout first. {player_name}', 409
    player_name = request.form['player_name']

    session['player_name'] = player_name
    current_app.logger.info(f'{player_name} logged in successfully.')
    if player_name not in current_app.players:
        current_app.players[player_name] = Player(player_name)
        current_app.logger.info(f'{player_name} sign in.')
    return f'Hello. {player_name}', 200


@app.route('/logout', methods=['POST'])
@check_login
@logger_decorator
def logout():
    player_name = session['player_name']
    if player_name not in current_app.players:
        current_app.logger.info(f'{player_name} already logged out.')
        return 'You are already logged out.', 409
    del current_app.players[player_name]
    session.clear()
    current_app.logger.info(f'{player_name} logged out successfully.')
    return f'Good bye. {player_name}', 200


@app.route('/remove_player', methods=['POST'])
@check_admin
@logger_decorator
def remove_player():
    player_name = request.form['player_name']
    if not player_name in current_app.players:
        return f'{player_name} does not exist.', 409
    del current_app.players[player_name]
    return 'Success.', 200


@app.route('/player', methods=['GET'])
@logger_decorator
def player():
    return jsonify(list(current_app.players.keys())), 200


@app.route('/make_match', methods=['POST'])
@check_admin
@logger_decorator
def make_match():
    if not ('black' in request.form and 'white' in request.form and request.form['black'] in current_app.players and request.form['white'] in current_app.players):
        return 'Invalid player.', 400

    black_name = request.form['black']
    white_name = request.form['white']

    black_player = current_app.players[black_name]
    white_player = current_app.players[white_name]

    if black_player.valid_game or white_player.valid_game:
        return 'Game is arleady started.', 409

    config = {}
    config['black'] = black_player
    config['white'] = white_player
    config['size'] = GRID_SIZE
    config['name'] = random_name(3, list(current_app.games.keys()))
    game = Game(config)
    current_app.games[config['name']] = game
    black_player.game = game
    white_player.game = game
    black_player.valid_game = True
    white_player.valid_game = True
    return f'Success. Game name: {config["name"]}'


@app.route('/state', methods=['GET'])
@check_login
@check_game_started
@logger_decorator
def state():
    player = current_app.players[session['player_name']]
    try:
        result = player.game.get_state(player.player_name)
    except InvalidTurnException:
        return 'Not your turn.', 403
    else:
        return jsonify(result), 200


@app.route('/action', methods=['POST'])
@check_login
@logger_decorator
def action():
    if 'y' not in request.form or 'x' not in request.form:
        return 'Bad Request.', 400

    player = current_app.players[session['player_name']]

    try:
        result = player.game.do_action(player.player_name, int(
            request.form['y']), int(request.form['x']))
    except InvalidActionException:
        return "Invalid Action", 409
    except InvalidTurnException:
        return 'Not your turn.', 403
    else:
        return jsonify(result), 200


@app.route('/match', methods=['GET'])
@logger_decorator
def match():
    result = {}
    for game in current_app.games.values():
        result[game.game_name] = game.serialize()
    return jsonify(result), 200


@app.route('/find_history', methods=['POST'])
@check_admin
@logger_decorator
def find_history():
    if 'game_name' not in request.form:
        return 'Bad Request.', 400

    if request.form['game_name'] not in current_app.games:
        return f"Can't find {request.form['game_name']}"

    return jsonify(current_app.games[request.form['game_name']].get_history()), 200


@app.route('/history', methods=['GET'])
@check_login
@check_game_started
@logger_decorator
def history():
    return jsonify(current_app.players[session['player_name']].game.get_history()), 200


def init_app():
    app.secret_key = os.urandom(12)
    app.players = {}
    app.games = {}
    app.logger.info(
        f'Server start. Host: {HOST} | Port: {PORT} | debug: {IS_DEBUG}')
    app.logger.info(f'secret_key: {app.secret_key}')
    app.run(host=HOST, debug=IS_DEBUG, port=PORT)


if __name__ == '__main__':
    init_app()
