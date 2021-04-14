import socket
import threading
import netman
import time


class Blaster:
    def __init__(self, port):
        self._alive = False
        self._port = port
        self.stations = {}
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._main_thread = None
        self._heartbeat_thread = None

    def start(self, async=True, daemon=True):
        self._alive = True
        try:
            self._server.bind(('', self._port))
            self._server.listen()
        except Exception as e:
            print("ERROR OCCURRED IN Blaster.start")
            print(str(e))
        if async:
            self._main_thread = threading.Thread(target=self._station_acceptor, args=(), daemon=daemon)
            self._main_thread.start()
        else:
            self._station_acceptor()
        self._start_heartbeat()

    def _station_acceptor(self):
        print("Blaster initiated successfully")
        while self._alive:
            print("Waiting for a station...")
            sock, addr = None, None
            try:
                sock, addr = self._server.accept()
                print("Blaster received connection from " + addr[0])
            except Exception as e:
                print("ERROR OCCURRED IN Blaster._station_accepter")
                print(str(e))
                time.sleep(2)
            if sock is not None and addr is not None:
                netman.sock_recv_async(self._on_station_connected, sock)

    # Each of these calls belongs to one station!
    # Calls are launched from separate threads, each thread, again, belonging to one station
    def _on_station_connected(self, sock, result):
        success = result[0]
        data = result[1]
        if not success: return

        maid = data.decode('ascii')
        self.stations[maid] = {'sock': sock}
        print("Added " + maid + " to list")

    def blast(self, maid, data):
        sock = self.stations.get(maid, {}).get('sock', None)
        success = netman.sock_send_sync(sock, data)
        print("Sent sequence to " + maid + " with status " + str(success))
        return success

    def blast_async(self, callback, maid, data):
        sock = self.stations.get(maid, {}).get('sock', None)
        netman.sock_send_async(callback, sock, data)

    def get_amount_connected(self):
        return len(self.stations)

    def check_on(self, maid):
        return self.blast(maid, netman.SEQ_PING)

    def _heartbeat(self):
        while self._alive:
            def processor(success):
                maid = threading.currentThread().getName()
                if success:
                    print(maid + " is alive")
                else:
                    print(maid + " is dead")
                    self.stations.pop(maid)
            for maid in self.stations:
                sock = self.stations.get(maid, {}).get('sock', None)
                netman.sock_send_async(processor, sock, netman.SEQ_PING, maid)
            for i in range(1800):
                time.sleep(1) # so that we dont get hanged
                if not self._alive: break

    def _start_heartbeat(self):
        self._heartbeat_thread = threading.Thread(target=self._heartbeat)
        self._heartbeat_thread.start()

    def stop(self):
        print("Stopping server...")
        self._alive = False
        for maid in self.stations:
            sock = self.stations.get(maid, {}).get('sock', None)
            if sock is not None:
                sock.send(netman.SEQ_DEATH)
                sock.close()
        self.stations = {}
        self._server.close()
        print("Stopped server")
