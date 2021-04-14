#!/usr/bin/env python3

import json
from flask import Flask, Request, Response, request
from blaster import *
from web import WebServer, res, suc, err
import time
import sys
import signal
from fireman import Fireman
from dbman import DBMan


fireman = Fireman()
blaster = Blaster(3001)
dbman = DBMan(fireman, blaster)
pictures = {}


def test():
    return res(200)


def register_user():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    if uid is None: return err("INVALID_TOKEN")
    fcm = d.get('fcm', None)
    name = d.get('name', None)
    dbman.register_user(uid, fcm, name)
    stations = dbman.get_user_stations(uid)
    return suc(stations)


def register_station():
    d = request.get_json(force=True)
    maid = fireman.verify_maid(d.get('maid', None))
    name = d.get('name', None)
    secret_code = d.get('secret_code', None)
    if type(maid) is not str: return err("INVALID_MAID")
    if type(name) is not str: return err("INVALID_NAME")
    if type(secret_code) is not str: return err("INVALID_SECRET_CODE")
    if maid not in blaster.stations: return err("SOCKET_DISCONNECTED")
    dbman.register_station(maid, name, secret_code)
    return suc()


def add_user_to_station():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    maid = fireman.verify_maid(d.get('maid', None))
    if not dbman.user_exists(uid): return err("INVALID_UID")
    if not dbman.station_exists(maid): return err("INVALID_MAID")
    dbman.add_user_to_station(uid, maid, -1)
    new_station = dbman.get_new_station(uid, maid)
    return suc(new_station)


def remove_user_from_station():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    maid = fireman.verify_maid(d.get('maid', None))
    if not dbman.user_exists(uid): return err("INVALID_UID")
    if not dbman.station_exists(maid): return err("INVALID_MAID")
    dbman.remove_user_from_station(uid, maid)
    return suc()


def fetch_station_users():
    d = request.get_json(force=True)
    maid = fireman.verify_maid(d.get('maid', None))
    last_updated = d.get('last_updated', 0)
    if not dbman.station_exists(maid): return err("INVALID_MAID")
    return suc(dbman.get_station_users_after(maid, last_updated))


def fetch_user_stations():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    if not dbman.user_exists(uid): return err("INVALID_UID")
    return suc(dbman.get_user_stations(uid))


def fetch_user_enrolls():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    maid = fireman.verify_maid(d.get('maid', None))
    if not dbman.user_exists(uid): return err("INVALID_UID")
    if not dbman.station_exists(maid): return err("INVALID_MAID")
    enrolls = dbman.get_enrolls_by_station(uid, maid)
    return suc({'enrolls': enrolls})


def unlock_remote():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    maid = fireman.verify_maid(d.get('maid', None))
    if type(maid) is not str: return err("INVALID_MAID")
    if type(uid) is not str: return err("INVALID_UID")
    if not dbman.user_belongs_to_station(uid, maid): return err("UNAUTHORIZED")
    success = blaster.blast(maid, netman.SEQ_UNLOCK)
    return suc() if success else err("UNLOCK_FAILED")


def unlock_physical():
    d = request.get_json(force=True)
    maid = fireman.verify_maid(d.get('maid', None))
    uid = d.get('uid', None)
    if type(maid) is not str: return err("INVALID_MAID")
    if type(uid) is not str: return err("INVALID_UID")
    if not dbman.user_belongs_to_station(uid, maid): return err("UNAUTHORIZED")
    fireman.send_message_to_uid(uid, "UNLOCKED")
    return suc()


def enroll_remote():
    d = request.get_json(force=True)
    return res(200)


def enroll_physical():
    d = request.get_json(force=True)
    return res(200)


def get_stream_image():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    maid = fireman.verify_maid(d.get('maid', None))
    if type(maid) is not str: return err("INVALID_MAID")
    if type(uid) is not str: return err("INVALID_UID")
    if not dbman.user_belongs_to_station(uid, maid): return err("USER_DOES_NOT_BELONG")
    blaster.blast(maid, netman.SEQ_STREAM)
    max_wait = 2
    waited = 0
    delay = 0.25
    while waited < max_wait:
        now = time.time()
        if pictures.get(maid, None) is None or now - pictures[maid]['received'] > 15:
            time.sleep(delay)
            waited += delay
        else:
            return suc(pictures[maid])
    return err("IMAGE_NOT_RECEIVED")


def upload_stream_image():
    d = request.get_json(force=True)
    maid = fireman.verify_maid(d.get('maid', None))
    if type(maid) is not str: return err("INVALID_MAID")
    print("Hue")
    png_base64 = d.get('png', None)
    if type(png_base64) is not str: return err("INVALID_PNG")
    print("HAA")
    pictures[maid] = {'picture': png_base64, 'received': time.time()}
    return suc()


def override_user_enrolls():
    d = request.get_json(force=True)
    uid = fireman.verify_uid(d.get('token', None))
    if type(uid) is not str: return err("INVALID_UID")
    enrolls = d.get('data', None)
    if type(enrolls) is not str: return err("INVALID_DATA")
    dbman.override_user_enrolls(uid, enrolls)
    return suc()




web_server = WebServer(3002)

web_server.add_handler(test, methods=['POST', 'GET'])
web_server.add_handlers([register_user, register_station, fetch_user_enrolls,
                         unlock_remote, unlock_physical, enroll_remote,
                         enroll_physical, get_stream_image, add_user_to_station,
                         remove_user_from_station, fetch_station_users, fetch_user_stations,
                         override_user_enrolls, upload_stream_image])

blaster.start()
web_server.start()


def signal_handler(sig, frame):
    print("Exiting gracefully...")
    blaster.stop()
    sys.exit(0)


print("Let's roll!")
print("CTRL+C to exit...")
signal.signal(signal.SIGINT, signal_handler)
signal.pause()

