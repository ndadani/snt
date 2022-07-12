
import socket


HOST = "127.0.0.1"
PORT = 0

class Server(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        self.socket.bind((self.hostname, self.port))
        print(self.socket.getsockname())
        self.socket.listen()

        conn, address = self.socket.accept()
        data = float(conn.recv(2048).decode('utf-8'))
        print(data)
        conn.sendall(str.encode(str(data).zfill(17)))
        conn.close()
        self.socket.close()

if __name__ == "__main__":
    server = Server(HOST, PORT)
    try:
        server.start()
    except Exception as e:
        print(e)