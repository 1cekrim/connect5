import requests
import time
import json
import multiprocessing as mp

from functools import wraps

host = 'http://3.133.86.107:80/'
ADMIN_PASSWORD = 'rla92233'

command_functions = {}
admin_sess = requests.Session()

mp.set_start_method('fork', force=True)


def is_success(rep):
    return rep.status_code // 100 == 2


def print_response(rep):
    if is_success(rep):
        valid = '[Success] '
    else:
        valid = '[Error] '
    print(valid + rep.text)


def print_json_response(rep):
    if is_success(rep):
        parsed = json.loads(rep.text)
        print(json.dumps(parsed, indent=4, sort_keys=True))
    else:
        print('[Error]')


def command_func(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('\n[Command Start]')
        func(*args, **kwargs)
        print('[Command End]\n')
    command_functions[func.__name__] = wrapper
    return wrapper


sessions = {}
@command_func
def make_session(command):
    if len(command) != 1:
        print('session [session name]')
    elif command[0] in sessions:
        print('[Error] Already exist.')
    else:
        sessions[command[0]] = requests.Session()
        print('[Result] Success.')


@command_func
def session(command):
    print(*list(sessions.keys()), sep='\n')


@command_func
def login(command):
    if len(command) != 2:
        print('login [session name] [player name]')
    elif command[0] not in sessions:
        print('[Error] Invalid session.')
    else:
        print_response(sessions[command[0]].post(host +
                                                 'login', {'player_name': command[1]}))


@command_func
def logout(command):
    if len(command) != 1:
        print('logout [session name]')
    elif command[0] not in sessions:
        print('[Error] Invalid session.')
    else:
        print_response(sessions[command[0]].post(host + 'logout'))


@command_func
def state(command):
    if len(command) != 1:
        print('state [session name]')
    elif command[0] not in sessions:
        print('[Error] Invalid session.')
    else:
        print_json_response(sessions[command[0]].get(host + 'state'))


@command_func
def make_match(command):
    if len(command) != 2:
        print('make_match [black player] [white player]')
    else:
        form = {}
        form['admin_password'] = ADMIN_PASSWORD
        form['black'] = command[0]
        form['white'] = command[1]
        print_response(admin_sess.post(host + 'make_match', form))


@command_func
def action(command):
    if len(command) != 3:
        print('action [session name] [x position] [y position]')
    else:
        form = {}
        form['y'] = int(command[2])
        form['x'] = int(command[1])
        print_response(sessions[command[0]].post(host + 'action', form))


@command_func
def match(command):
    if len(command) != 0:
        print('match')
    else:
        print_json_response(admin_sess.get(host + 'match'))


@command_func
def history(command):
    if len(command) != 1:
        print('history [session name]')
    else:
        print_json_response(sessions[command[0]].get(host + 'history'))


def connect_inter(current_match, form):
    import connect5_viewer
    size = int(current_match['column_size'])
    viewer = connect5_viewer.Connect5Viewer(
        current_match['game_name'], size, 10, 5)

    def main_loop():
        rep = admin_sess.post(host + 'find_history', form)
        if not is_success(rep):
            print("Can't find history")
            return
        viewer.update_history(rep.json())
        time.sleep(1)

    viewer.show(main_loop)


@command_func
def connect(command):
    if len(command) != 1:
        print('connect [match name]')

    form = {}
    form['admin_password'] = ADMIN_PASSWORD
    form['game_name'] = command[0]

    match_rep = admin_sess.get(host + 'match')
    if not is_success(match_rep):
        print('Invalid?')

    matches = match_rep.json()

    if command[0] not in matches:
        print('Invalid match.')
        print(matches)
        return

    current_match = matches[command[0]]

    if current_match['column_size'] != current_match['row_size']:
        print('column_size not equal row_size.')

    print('[Info] Success.')
    print(f"Game name: {current_match['game_name']}")
    print(f"Black: {current_match['black_player_name']}")
    print(f"White: {current_match['white_player_name']}")

    p = mp.Process(target=connect_inter, args=(current_match, form))
    p.daemon = True
    p.start()


@command_func
def player(command):
    if len(command) != 0:
        print('player')

    player = admin_sess.get(host + 'player')
    if not is_success(player):
        print('Invalid?')
    print_json_response(player)


while True:
    command = str(input())
    if command == 'exit':
        print('exit.')
        break
    if command.split(' ')[0] not in command_functions:
        print('Invalid command.')
        continue
    command_functions[command.split(' ')[0]](command.split(' ')[1:])
