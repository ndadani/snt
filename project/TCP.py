import threading
import socket

class Node(object):

    def __init__(self, hostname, port=0):
        self.hostname = hostname
        self.port = port

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.hostname, self.port))    #if we bind to port 0, the OS will pick an available port
            self.port = self.socket.getsockname()[1]
            print(self.port)
            self.socket.listen(1)
        except Exception as e:
            print(e)

