#!/usr/bin/env python3

from fireman import *
from pymongo import MongoClient

client = MongoClient()
interstellar = client.interstellar
interstation = client.interstation

def cleanse():
    interstellar['users'].delete_many({})
    interstellar['machines'].delete_many({})
    interstellar['relationships'].delete_many({})
    interstation['users'].delete_many({})

def printstellar(table):
    cursor = interstellar[table].find({})
    for entry in cursor: print(entry)

def printstation(table):
    cursor = interstation[table].find({})
    for entry in cursor: print(entry)

printstation('users')

cleanse()