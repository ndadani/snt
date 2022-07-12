import threading
import socket

def handle(connection):
    try:
        while True:
            data = connection.recv(2048)
            print(data)
            connection.send(data)
    except:
        pass
    finally:
        connection.close()

class Node(object):

    def __init__(self, hostname, port=0):
        self.hostname = hostname
        self.port = port

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
            #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.hostname, self.port))    #if we bind to port 0, the OS will pick an available port
            self.port = self.socket.getsockname()[1]
            # print(self.port)
            self.socket.listen()

            while True:
                conn, address = self.socket.accept()
                # t = threading.Thread(target=handle, args=(conn, ))
                # t.daemon = True
                # t.start()

        except Exception as e:
            print(e)


#TODO build the connection handlers
#TODO close


