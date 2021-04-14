#!/usr/bin/env python3

from commander import Commander
import netman
import time
from camera import Camera
from PyRedactedCompanyName import *
import threading
import cv2

MAID = "VCZSD" #fetch maid from file

commander = Commander()
rcn = RedactedCompanyNameSdk("1234123412341234", "RedactedLicense", debug=True)
rcn.set_image_params(480, 640)
camera = Camera(1)
camera.start()
rcn.initUser("local")


class Meta:
    def __init__(self): pass
meta = Meta()


meta.last_pinged = 0
def ping():
    meta.last_pinged = time.time()


def unlock():
    print("Simulated Unlock")


def fetch():
    print("Fetching users")
    users = commander.fetch_users()
    rcn.load_enrolls(str(users))



def stream():
    png = camera.get_png()
    commander.send_stream(png)


commander.add_handler(netman.SEQ_PING, ping)
commander.add_handler(netman.SEQ_UNLOCK, unlock)
commander.add_handler(netman.SEQ_FETCH, fetch)
commander.add_handler(netman.SEQ_STREAM, stream)


def refresher():
    meta.last_pinged = 0
    while True:
        if time.time() - meta.last_pinged > 1800*1.1 or not commander.connected:
            print("Refreshing connection")
            meta.connected = False
            while not meta.connected:
                meta.connected = commander.connect(MAID, "REDACTEDSTREETADDRESS", "DINGDONG")
                if not meta.connected:
                    print("Could not connect. Retrying in 5s...")
                    time.sleep(5)
                else:
                    print("Connection established successfully!")
                    fetch()
                    meta.last_pinged = time.time()
        time.sleep(10)
thread_refresher = threading.Thread(target=refresher)
thread_refresher.start()

while True:
    mat = camera.get_mat()
    if mat is None: continue
    res = rcn.match_all(mat)
    print(res)
    time.sleep(0.25)
