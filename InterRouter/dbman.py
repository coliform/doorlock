from pymongo import MongoClient
import time
import netman


class DBMan:
    def __init__(self, fireman, blaster):
        self._client = MongoClient()
        self._db = self._client.interstellar
        self._fireman = fireman
        self._blaster = blaster

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
            self._db[table].find_one_and_update({"uid": uid}, {"$set": data})

    def _post_field(self, table, uid, field, value):
        entry = self._get(table, uid)
        entry[field] = value
        self._post(table, uid, entry)

    def _get(self, table, uid):
        return self._db[table].find_one({'uid':uid})

    def _get_field(self, table, uid, field):
        item = self._get(table, uid)
        if item is None: return {}
        return item[field]

    def _post_relationship(self, uid, maid, valid_until=None):
        last_updated = time.time()
        key = {'uid': uid, 'maid': maid}
        properties = dict({
            'last_updated': last_updated,
        }, **key)
        if valid_until is not None: properties['valid_until'] = valid_until
        if self._get_relationship(uid, maid):
            self._db['relationships'].find_one_and_update(key, {'$set': properties})
        else:
            self._db['relationships'].insert_one(properties)

    def _get_relationship(self, uid, maid):
        return self._db['relationships'].find_one({'uid': uid, 'maid': maid})

    def user_belongs_to_station(self, uid, maid):
        relationship = self._get_relationship(uid, maid)
        if not relationship: return False
        valid_until = relationship['valid_until']
        if valid_until == -1: return True
        elif valid_until < time.time(): return False
        else: return True
        '''        relationship = self._get_relationship(uid, maid)
        if not relationship or \
                (relationship['valid_until'] != -1 and relationship['valid_until'] < time.time()):
            return None'''

    def get_user_stations(self, uid):
        cursor = self._db['relationships'].find({'uid': uid})
        stations = {}
        for station in cursor:
            maid = station['maid']
            if not self.user_belongs_to_station(uid, maid): continue
            name = self._get_field('stations', maid, 'name')
            stations[maid] = {'name': name, 'valid_until': station['valid_until']}
        return stations

    def get_station_users_after(self, maid, last_updated):
        print("Requesting users for {} after {}".format(maid, last_updated))
        cursor = self._db['relationships'].find({'maid': maid, 'last_updated': {'$gt': last_updated}})
        users = {}
        for user in cursor:
            uid = user['uid']
            enrolls = self._get_field('users', uid, 'enrolls')
            users[uid] = {'enrolls': enrolls, 'valid_until': user['valid_until']}
        return users

    def get_users_after(self, maid, last_updated):
        return self._db['relationships'].find(
            {'maid': maid, 'last_updated': {'$gt':last_updated}},
            {'maid': 0, 'uid': 1, 'valid_until': 1, 'last_updated': 1})

    def announce_modified(self, uid, maid=None):
        stations = self.get_user_stations(uid)
        if maid is None:
            for maid in stations:
                self._post_relationship(uid, maid)
                self._blaster.blast(maid, netman.SEQ_FETCH)
        else:
            self._blaster.blast(maid, netman.SEQ_FETCH)

    def get_enrolls_by_station(self, uid, maid):
        if not self.user_belongs_to_station(uid, maid): return False
        return self._get_field('users', uid, 'enrolls')

    def user_exists(self, uid):
        return not not self._get('users', uid)

    def station_exists(self, maid):
        return not not self._get('stations', maid)

    def register_user(self, uid, fcm=None, name=None):
        user = self._get('users', uid)
        if not user:
            if fcm is None: fcm = ''
            if name is None: name = 'Anonymous'
            self._post('users', uid, {'fcm': fcm, 'name': name, 'enrolls': ''})
        elif fcm or name:
            if fcm: user['fcm'] = fcm
            if name: user['name'] = name
            self._post('users', uid, user)

    def register_station(self, maid, name, secret_code):
        station_data = self._get('stations', maid)
        if not station_data:
            data = {'name': name, 'secret_code': secret_code}
            self._post('stations', maid, data)
        elif station_data['secret_code'] != secret_code:
            return

    def add_user_to_station(self, uid, maid, valid_until=-1):
        self._post_relationship(uid, maid, valid_until)
        self.announce_modified(uid, maid)

    def get_new_station(self, uid, maid):
        if not self.user_belongs_to_station(uid, maid): return {}
        name = self._get_field('stations', maid, 'name')
        valid_until = self._get_relationship(uid, maid)['valid_until']
        return {'name': name, 'valid_until': valid_until}

    def remove_user_from_station(self, uid, maid):
        self.add_user_to_station(uid, maid, 0)

    def override_user_enrolls(self, uid, enrolls):
        self._post_field('users', uid, 'enrolls', enrolls)
        self.announce_modified(uid)

