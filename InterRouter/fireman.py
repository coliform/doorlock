import firebase_admin
from firebase_admin import credentials, db, auth


class Fireman:
    def __init__(self):
        cred = credentials.Certificate("venv/interstellar.json")
        firebase_admin.initialize_app(cred, {'databaseURL': 'https:/REDACTED.firebaseio.com'})


    def post(self, path, data):
        db.reference(path).set(data)

    def get(self, path):
        return db.reference(path).get()


    '''def verify_uidtoken(self, uidtoken):
        try:
            seg = uidtoken.split("_")
            if len(seg) != 2: return None
            decoded_token = auth.verify_id_token(seg[1])
            uid = decoded_token.get('uid', None)
            if seg[0] == uid: return uid'''


    def verify_uid(self, id_token):
        #return id_token
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token.get('uid', None)
        except Exception as e:
            print("ERROR OCCURRED IN Fireman.verify_uid")
            print(str(e))
            return None

    def verify_maid(self, maid):
        return maid #TODO

    def send_message_to_uid(self, uid, message):
        pass
