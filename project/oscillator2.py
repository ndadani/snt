import socket
import numpy

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 6543  # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.sendall(bytes(20))
data = s.recv(1024)
print(f"Received {data!r}")
dphi = 20 + 7 * numpy.sin((20 - int.from_bytes(data,"little"))*numpy.pi/180)
s.sendall(dphi)
