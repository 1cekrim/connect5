from flask import Flask, request, current_app, session, escape
import os

app = Flask(__name__)
admin_password = 'rla92233'


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
def logout():
    if not 'player_name' in session:
        return f'Please login first.'
    player_name = session['player_name']
    session.pop('player_name', None)
    if not player_name in current_app.players:
        return 'You are already logged out.'
    del current_app.players[player_name]
    return f'Good bye. {player_name}'


@app.route('/remove_player', methods=['post'])
def remove_player():
    if request.form['admin_password'] != admin_password:
        return 'Access denied.'
    player_name = request.form['player_name']
    if not player_name in current_app.players:
        return f'{player_name} does not exist.'
    del current_app.players[player_name]
    return 'Success.'


def init_app():
    app.secret_key = os.urandom(12)
    app.players = {}
    app.run(host='127.0.0.1', debug=True, port=12345)


class Player:
    def __init__(self, player_name: str):
        self.player_name = player_name


if __name__ == '__main__':
    init_app()
