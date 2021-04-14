import requests
import socket
import netman
import threading
import time
import json
from dbman import DBMan
import base64


IP_COMMAND_CENTER = "127.0.0.1"
URL_COMMAND_CENTER = "http://" + IP_COMMAND_CENTER + ":3002/"
URL_REGISTER_MACHINE = URL_COMMAND_CENTER + "register_station.rcn"
URL_FETCH_USER       = URL_COMMAND_CENTER + "fetch_user_by_station.rcn"
URL_UNLOCK_PHYSICAL = URL_COMMAND_CENTER + "register_station.rcn"
PATH_REGISTER_MACHINE = "register_station"
PATH_FETCH_USERS = "fetch_station_users"
PATH_FETCH_USER_ENROLLS = "fetch_user_enrolls"
PATH_STREAM_IMAGE = "upload_stream_image"


def post(path, data):
    url = URL_COMMAND_CENTER + path + ".rcn"
    response = requests.post(url, json=data)
    return response.status_code, json.loads(str(response.text))


def post_async(callback, path, data):
    def internal(callback, path, data):
        print(path)
        print(data)
        status_code, content = post(path, data)
        if callback is not None: callback(status_code, content)
    thread = threading.Thread(target=internal, args=(callback, path, data))
    thread.start()
    return thread


class Commander:
    def __init__(self):
        self.connected = False
        self._listen_to_commands_thread = None
        self._sequences = {}
        self._dbman = DBMan()

    def connect(self, maid, name, secret_code):
        self.connected = False
        self._maid = maid
        self._secret_code = secret_code
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((IP_COMMAND_CENTER, 3001))
        except Exception as e:
            print("ERROR OCCURRED IN Commander.connect")
            print(str(e))
            return False
        success = netman.sock_send_sync(self._sock, maid.encode('ascii'))
        if not success:
            print("ERROR OCCURRED IN Commander.connect")
            print("Socket did not accept maid")
            self._sock.close()
            return False
        data = {
            'maid': maid,
            'name': name,
            'secret_code': secret_code
        }
        response = requests.post(URL_REGISTER_MACHINE, json=data)
        if response.status_code != 200:
            print("ERROR OCCURRED IN Commander.connect")
            print("Could not register - ")
            print(response.status_code)
            print(response.content)
        self._listen_to_commands_thread = threading.Thread(target=self._listen_to_commands, daemon=True)
        self._listen_to_commands_thread.start()
        self.connected = True
        #self._sequences[netman.SEQ_FETCH]()
        return True

    def add_handler(self, sequence, handler):
        self._sequences[sequence] = handler

    def _listen_to_commands(self):
        error_counter = 0
        while error_counter < 10:
            status, data = netman.sock_recv_sync(self._sock)
            if status == False:
                error_counter += 1
                continue
            self._command_processor(data)
        self.connected = False
        self._sock.close()
        print("Connection dropped")

    def _command_processor(self, sequence):
        if sequence not in self._sequences: return False
        self._sequences[sequence]()

    def fetch_users(self):
        status_code, users = post(PATH_FETCH_USERS, {'maid': self._maid})
        for uid in users:
            enrolls = users[uid]['enrolls']
            valid_until = users[uid]['valid_until']
            self._dbman.update_user(uid, valid_until, enrolls)
        self._dbman.delete_redundant()
        return self._dbman.get_all_user_enrolls()

    def send_stream(self, png):
        payload = {'maid': self._maid, 'png': ''}
        if png is not None: payload['png'] = base64.urlsafe_b64encode(png).decode("utf-8")
        def send_stream_thread(payload):
            requests.post(URL_COMMAND_CENTER + PATH_STREAM_IMAGE + ".rcn", json=payload)
        threading.Thread(target=send_stream_thread, args=(payload,)).start()

