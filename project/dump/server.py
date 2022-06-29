import threading
import socket
import queue

HOST = "127.0.0.1"
PORT = 0  # Port to listen on (non-privileged ports are > 1023)

_sentinel = "STOP" # A sentinel to put on the queue to indicate completion

def handle_recv(connection,q):
    while True:
        data = connection.recv(2048)
        q.put(data)
        if not data:
            break
    q.put(_sentinel)
    connection.close()


def handle_send(connection,q):
    while True:
        data = q.get()
        if data is _sentinel:
            q.put(_sentinel)
            break
        connection.sendall(data)
    connection.close()


class Server(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        print(self.socket.getsockname())
        self.socket.listen()

        q = queue.Queue()
        thread_list = []
        while True:
            conn, address = self.socket.accept()
            t1 = threading.Thread(target=handle_recv, args=(conn, q))
            thread_list.append(t1)
            t1.daemon = True
            t2 = threading.Thread(target=handle_send, args=(conn, q))
            thread_list.append(t2)
            t2.daemon = True
            t1.start()
            t2.start()

            msg=input()
            if msg=='END':
                break
            elif msg=='NOW':
                conn.sendall(str.encode(msg))

        self.socket.close()
        for t in thread_list:
            t.join()

if __name__ == "__main__":
    server = Server(HOST, PORT)
    try:
        server.start()
    except Exception as e:
        print(e)














# import multiprocessing
# import socket

# HOST = "127.0.0.1"
# PORT = 9001  # Port to listen on (non-privileged ports are > 1023)

# def handle(connection, address):
#     try:
#         while True:
#             data = connection.recv(1024)
#             connection.sendall(data)
#     except:
#         pass
#     finally:
#         connection.close()

# class Server(object):

#     def __init__(self, hostname, port):
#         self.hostname = hostname
#         self.port = port

#     def start(self):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.socket.bind((self.hostname, self.port))
#         self.socket.listen()

#         while True:
#             conn, address = self.socket.accept()
#             process = multiprocessing.Process(target=handle, args=(conn, address))
#             process.daemon = True
#             process.start()

# if __name__ == "__main__":
#     server = Server(HOST, PORT)
#     try:
#         server.start()
#     except Exception as e:
#         print(e)
#     finally:
#         for process in multiprocessing.active_children():
#             process.terminate()
#             process.join()



