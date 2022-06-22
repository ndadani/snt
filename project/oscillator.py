import socket
import numpy
import struct
import threading
import time


SOCKET_AMOUNT = 2
HOST = "127.0.0.1"  # localhost
PORT = 9001  # The port used by the server

def oscillator(ip, port, omega, k):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #TCP
    s.connect((ip, port))
    send = struct.pack('f',omega)
    s.sendall(send)
    data = struct.unpack('f',s.recv(1024))
    print(data)
    dphi = omega + k * numpy.sin((omega - data[0])*numpy.pi/180)
    print(dphi)
    s.sendall(dphi)
    s.close()


if __name__ == "__main__":
    thread_list = []
    for i in range(SOCKET_AMOUNT):
        client_thread = threading.Thread(target=oscillator, args=(HOST, PORT, i*10, i))
        client_thread.setDaemon(True)
        thread_list.append(client_thread)
        client_thread.start()

    waiting = time.time()
    [x.join() for x in thread_list]
    

