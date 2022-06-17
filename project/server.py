import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 6543  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()

print(f"Connected by {addr}")
while True:
    data = conn.recv(1024)
    if not data:
        break
    conn.sendall(data)
s.close()

































# import socket

# s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# s.bind(('localhost',9999))
# # Since the socket is server and client is on same machine
# # we can use 'localhost'
# # 9999 is the port number used for binding.
# s.listen()
# # This listens to only three clients.
# while True:
#     oscillator, address_client = s.accept()
#     oscillator.send("lkejfd")
#     oscillator.close()

# socket_object=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# # Socket Object is created using AF_INET and TCP.
# socket_object.bind(('localhost',9999))
# # Since the socket is server and client is on same machine
# # we can use 'localhost'
# # 9999 is the port number used for binding.
# socket_object.listen(3)
# # This listens to only three clients.
# while True:
#     client_object, address_client = socket_object.accept()
#     client_object.send(bytes("You are connected to Server..",'utf-8'))
#     print(client_object.recv(1024))
#     client_object.close()
    
