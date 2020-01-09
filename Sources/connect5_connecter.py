import requests
import time


class Connect5Connecter:
    def __init__(self, url: str, name: str):
        self.url = url
        self.name = name
        self.sess = requests.Session()
        self.login(self.name)

    def login(self, name: str):
        assert Connect5Connecter.is_success(self.sess.post(
            self.url + 'login', {'player_name': name}))

    @classmethod
    def is_success(cls, rep):
        return rep.status_code // 100 == 2

    def get_state(self, delay=1):
        while True:
            rep = self.sess.get(self.url + 'state')
            if Connect5Connecter.is_success(rep):
                return rep.json()
            time.sleep(delay)

    def send_action(self, column: int, row: int):
        assert self.sess.post(self.url + 'action',
                              {'x': column - 1, 'y': row - 1})
