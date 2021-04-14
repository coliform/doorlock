import cv2
import threading
import time

class Camera:
    def __init__(self, source):
        self._cap = cv2.VideoCapture(source)
        self._cap.set(3, 640)
        self._cap.set(4, 480)
        self._keep_going = False
        self._read_thread = None
        self._mat = None

    def stop(self):
        if self._read_thread is not None:
            self._keep_going = False
            time.sleep(0.5)
            self._read_thread = None

    def start(self):
        self.stop()
        self._keep_going = True
        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.start()

    def _read_loop(self):
        while self._keep_going:
            self._mat = self._cap.read()
            #print(self._cap.read())
            time.sleep(0.2)

    def get_mat(self):
        if self._mat is not None: return self._mat[1].copy()
        else: return None

    def get_png(self):
        return cv2.imencode('.png', self.get_mat())[1].tobytes()