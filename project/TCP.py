import socket
import time

class Node(object):

    def __init__(self, hostname, port=0):
        self.hostname = hostname
        self.port = port

    def start(self,o,to):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.hostname, self.port))    #if we bind to port 0, the OS will pick an available port
            self.port = self.socket.getsockname()[1]
            self.socket.listen()
            while True:
                try :
                    conn, address = self.socket.accept()
                    with conn:
                        data = conn.recv(2048)
                        # ti = int(round(time.time() * 1000))
                        # msg = str(o.id)+str(int(o.omega)*(ti-to))
                        # self.socket.send(str.encode(msg.zfill(17)))
                        print(data)
                        conn.send(data)
                except Exception as e :
                    conn, address = self.socket.accept()



