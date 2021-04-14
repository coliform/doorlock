from pymongo import MongoClient
import time
import json


class DBMan:
    def __init__(self):
        self._client = MongoClient()
        self._db = self._client.interstation
        self._enrolls = ""

    def _delete(self, table, uid):
        print("Deleting " + str(uid) + " from " + str(table))
        self._db[table].delete_one({'uid':uid})

    def _post(self, table, uid, data):
        print("Posting , data is " )
        print(data)
        print(self._get(table, uid))
        if not self._get(table, uid): self._db[table].insert_one(dict({'uid':uid}, **data))
        else:
            print("Welcome back " + uid)
            self._db[table].find_one_and_update({"uid":uid}, {"$set": data})

    def _post_field(self, table, uid, field, value):
        entry = self._get(table, uid)
        entry[field] = value
        self._post(table, uid, entry)

    def _get(self, table, uid):
        return self._db[table].find_one({'uid':uid})

    def _get_field(self, table, uid, field):
        return self._get(table, uid)[field]

    def update_user(self, uid, valid_until, enrolls):
        if valid_until == -2: self._delete('users', uid)
        else: self._post('users', uid, {'valid_until': valid_until, 'enrolls': enrolls, 'last_updated': time.time()})

    def delete_redundant(self):
        cursor = self._db['users'].find({})
        for user in cursor:
            uid = user['uid']
            valid_until = user['valid_until']
            if valid_until != -1 and valid_until < time.time():
                self._delete('users', uid)

    def get_user_enrolls(self, uid):
        return self._get('users', uid)['enrolls']

    def get_all_user_enrolls(self):
        users = {}
        cursor = self._db['users'].find({})
        for user in cursor: users[user['uid']] = user['enrolls']
        return json.dumps(users)

