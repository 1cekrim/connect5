import requests
from functools import wraps

host = 'http://127.0.0.1:12345/'
ADMIN_PASSWORD = 'rla92233'

command_functions = {}


def print_response(rep):
    if rep.status_code // 100 == 2:
        valid = '[Success] '
    else:
        valid = '[Error] '
    print(valid + rep.text)


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
        print_response(sessions[command[0]].get(host + 'state'))


while True:
    command = str(input())
    if command == 'exit':
        print('exit.')
        break
    if command.split(' ')[0] not in command_functions:
        print('Invalid command.')
        continue
    command_functions[command.split(' ')[0]](command.split(' ')[1:])
