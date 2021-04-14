import threading
from flask import Flask, Response
import json


ENDPOINT_FORMAT = '/{}.rcn'


def res(code, dic={}):
    response = Response(response=json.dumps(dic), status=code, mimetype='application/json')
    print("Responding with {0}".format(response))
    return response


def suc(dic={}):
    print(type(dic))
    return res(200,dic)


def err(val):
    print(val)
    return res(400,{'ERROR':val})


class WebServer:
    def __init__(self, port):
        self._app = Flask(__name__)
        self._port = port
        self._main_thread = None

    def start(self, async=True, daemon=True):
        try:
            if async:
                def runner(app, port): app.run('0.0.0.0', port, threaded=True)
                self._main_thread = threading.Thread(target=runner, args=(self._app, self._port), daemon=daemon)
                self._main_thread.start()
                print("Web server initiated successfully")
            else:
                self._app.run('0.0.0.0', self._port, threaded=True)
        except Exception as e:
            print("ERROR OCCURRED IN WebServer.start")
            print(str(e))

    def add_handler(self, handler=None, methods=None):
        name = handler.__name__
        endpoint = ENDPOINT_FORMAT.format(name)
        if methods is None: methods = ['POST']
        self._app.add_url_rule(endpoint, name, handler, methods=methods)

    def add_handlers(self, handlers):
        for handler in handlers: self.add_handler(handler)

