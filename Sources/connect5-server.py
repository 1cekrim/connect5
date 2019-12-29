import os
import string
import random
import numpy as np

from functools import wraps, reduce
from flask import Flask, request, current_app, session, escape, jsonify

app = Flask(__name__)
ADMIN_PASSWORD = 'rla92233'
GRID_SIZE = 5


class Player:
    def __init__(self, player_name: str):
        self.player_name = player_name


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
        self.grid = np.zeros((self.column_size, self.row_size))

    def get_state(self, player_name: str):
        if self.current_player.player_name != player_name:
            raise InvalidTurnException

        state = {}
        state['column_size'] = self.column_size
        state['row_size'] = self.row_size
        state['grid'] = self.grid.tolist()

        return state


def random_name(length, lst):
    strs = string.ascii_letters + string.digits
    while True:
        result = ""
        for _ in range(length):
            result += random.choice(strs)
        if lst and result not in lst:
            return result


def check_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'player_name' in session:
            return 'Please login first', 401
        if not session['player_name'] in current_app.players:
            return 'Session has expired.', 401
        return func(*args, **kwargs)
    return wrapper


def check_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'admin_password' in request.form:
            return 'Bad Request.', 400
        if request.form['admin_password'] != ADMIN_PASSWORD:
            return 'Access denied.', 403
        return func(*args, **kwargs)
    return wrapper


def check_game_started(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_app.players[session['player_name']]:
            return 'Game did not start.', 409
        return func(*args, **kwargs)
    return wrapper 


@app.route('/login', methods=['POST'])
def login():
    if 'player_name' in session:
        return f'Please logout first. {escape(session["player_name"])}', 409
    player_name = request.form['player_name']
    if player_name in current_app.players:
        return f'{player_name} is in conflict.', 409

    session['player_name'] = player_name
    current_app.players[player_name] = Player(player_name)
    return f'Hello. {player_name}', 200


@app.route('/logout', methods=['POST'])
@check_login
def logout():
    player_name = session['player_name']
    session.pop('player_name', None)
    if not player_name in current_app.players:
        return 'You are already logged out.', 409
    del current_app.players[player_name]
    return f'Good bye. {player_name}', 200


@app.route('/remove_player', methods=['POST'])
@check_admin
def remove_player():
    player_name = request.form['player_name']
    if not player_name in current_app.players:
        return f'{player_name} does not exist.', 409
    del current_app.players[player_name]
    return 'Success.', 200


@app.route('/player', methods=['GET'])
def player():
    return jsonify(list(current_app.players.keys())), 200


@app.route('/make_match', methods=['POST'])
@check_admin
def make_match():
    if not ('black' in request.form and 'white' in request.form and request.form['black'] in current_app.players and request.form['white'] in current_app.players):
        return 'Invalid player.', 400
    config = {}
    config['black'] = request.form['black']
    config['white'] = request.form['white']
    config['size'] = GRID_SIZE
    config['name'] = random_name(3, list(current_app.games.keys()))
    game = Game(config)
    current_app.games[config['name']] = game
    current_app.players[config['black']].game = game
    current_app.players[config['white']].game = game


@app.route('/state', methods=['GET'])
@check_login
def state():
    player = current_app.players[session['player_name']]
    try:
        result = player.game.get_state(player.player_name)
    except InvalidTurnException:
        return 'Not your turn.', 403
    else:
        return jsonify(result), 200


def init_app():
    app.secret_key = os.urandom(12)
    app.players = {}
    app.games = {}
    app.run(host='127.0.0.1', debug=True, port=12345)


if __name__ == '__main__':
    init_app()
