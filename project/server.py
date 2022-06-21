import socket
import struct

HOST = "127.0.0.1"
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()
print(f"Connected by {addr}")

while True:
    data = conn.recv(1024)
    if not data:
        print("break")
        break
    print(f"Received {data!r}")
    conn.sendall(data)
s.close()









