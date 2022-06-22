import multiprocessing
import socket
import time

HOST = "127.0.0.1"
PORT = 9001  # Port to listen on (non-privileged ports are > 1023)

def handle(connection, address):
    try:
        while True:
            data = connection.recv(1024)
            connection.sendall(data + ' server time {}'.format(time.time()))
    except:
        pass
    finally:
        connection.close()

class Server(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen()
# conn, addr = s.accept()
# print(f"Connected by {addr}")

# while True:
#     data = conn.recv(1024)
#     if not data:
#         print("break")
#         break
#     print(f"Received {data!r}")
#     conn.sendall(data)
# s.close()


if __name__ == "__main__":
    server = Server(HOST, PORT)
    try:
        server.start()
    except:
        print('Exception')
    finally:
        for process in multiprocessing.active_children():
            process.terminate()
            process.join()






