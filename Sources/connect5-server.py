import os

from functools import wraps, reduce
from flask import Flask, request, current_app, session, escape

app = Flask(__name__)
admin_password = 'rla92233'


def check_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not 'player_name' in session:
            return 'Please login first'
        if not session['player_name'] in current_app.players:
            return 'Session has expired.'
        return func(*args, **kwargs)
    return wrapper


@app.route('/login', methods=['POST'])
def login():
    if 'player_name' in session:
        return f'Please logout first. {escape(session["player_name"])}'
    player_name = request.form['player_name']
    if player_name in current_app.players:
        return f'{player_name} is in conflict.'

    session['player_name'] = player_name
    current_app.players[player_name] = Player(player_name)
    return f'Hello. {player_name}'


@app.route('/logout', methods=['POST'])
@check_login
def logout():
    player_name = session['player_name']
    session.pop('player_name', None)
    if not player_name in current_app.players:
        return 'You are already logged out.'
    del current_app.players[player_name]
    return f'Good bye. {player_name}'


@app.route('/remove_player', methods=['POST'])
def remove_player():
    if request.form['admin_password'] != admin_password:
        return 'Access denied.'
    player_name = request.form['player_name']
    if not player_name in current_app.players:
        return f'{player_name} does not exist.'
    del current_app.players[player_name]
    return 'Success.'


@app.route('/player', methods=['GET'])
def player():
    return reduce(lambda a, b: a + ' ' + b, current_app.players.keys(), '')


def init_app():
    app.secret_key = os.urandom(12)
    app.players = {}
    app.run(host='127.0.0.1', debug=True, port=12345)


class Player:
    def __init__(self, player_name: str):
        self.player_name = player_name


if __name__ == '__main__':
    init_app()
