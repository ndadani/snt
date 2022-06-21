import socket
import numpy
import struct

def oscillator(omega, k):
    HOST = "127.0.0.1"  # localhost
    PORT = 65432  # The port used by the server

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #TCP
    s.connect((HOST, PORT))
    send = struct.pack('f',omega)
    s.sendall(send)
    data = struct.unpack('f',s.recv(1024))
    print(data)
    dphi = omega + k * numpy.sin((omega - data[0])*numpy.pi/180)
    print(dphi)
    s.sendall(dphi)
    s.close()

if __name__ == '__main__': 
    # for i in range(10):
    #     print(i)
    #     oscillator(i*10,i)
    oscillator(100,5)





