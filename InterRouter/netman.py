import struct
import socket
import threading


SEQL = 128
def seq(num): return bytes([num]*SEQL)

SEQ_ACK    = seq(88)
SEQ_END    = seq(69)
SEQ_PING   = seq(42)
SEQ_DEATH  = seq(99)

SEQ_UNLOCK = seq(10)
SEQ_FETCH  = seq(11)
SEQ_ENROLL = seq(12)
SEQ_STREAM = seq(13)


def _sock_recv(sock):
    header = sock.recv(4)
    length = struct.unpack('>i', header)[0]
    data = sock.recv(length)
    try:
        sock.send(SEQ_ACK)
    except Exception as e:
        return False, data
    return True, data


def _sock_send(sock, data):
    length = len(data)
    header = struct.pack('>i', length)
    sock.send(header)
    sock.send(data)
    ack = sock.recv(SEQL)
    return ack == SEQ_ACK


def sock_recv_sync(sock):
    success, data = False, None
    try:
        success, data = _sock_recv(sock)
    except Exception as e:
        print("ERROR OCCURRED IN sock_recv_sync(sock)")
        print(str(e))
    return success, data


def sock_send_sync(sock, data):
    success = False
    try:
        success = _sock_send(sock, data)
    except Exception as e:
        print("ERROR OCCURRED IN sock_send_sync(sock)")
        print(str(e))
    return success


def sock_recv_async(callback, sock, thread_name=None):
    def _sock_recv_thread(callback, sock):
        callback(sock, sock_recv_sync(sock))
    if thread_name is not None:
        thread = threading.Thread(name=thread_name, target=_sock_recv_thread, args=(callback, sock))
    else:
        thread = threading.Thread(target=_sock_recv_thread, args=(callback, sock))
    thread.start()
    return thread


def sock_send_async(callback, sock, data, thread_name=None):
    def _sock_send_thread(callback, sock, data):
        callback(sock_send_sync(sock, data))
    if thread_name is not None:
        thread = threading.Thread(name=thread_name, target=_sock_send_thread, args=(callback, sock, data))
    else:
        thread = threading.Thread(target=_sock_send_thread, args=(callback, sock, data))
    thread.start()
    return thread

