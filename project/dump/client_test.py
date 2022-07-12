
import socket


HOST = "127.0.0.1"
PORT = 52303


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #TCP
s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

try:
    s.connect((HOST, PORT))
    msg = '1'
    s.sendall(str.encode(msg.zfill(17))) 
    # à droite dans le cas d'un float : msg.ljust(length, '0')
    # s.sendall(str.encode('1.111111111111111')) vvvvvvvvvvvv
    # s.sendall(str.encode('1.1111111111111111'))
    # s.sendall(str.encode('1.1111111111111112'))
    # s.sendall(str.encode('1.111111111111111111111111111'))
    # s.sendall(str.encode('1.1111111111111112'))
    
    data = s.recv(2048).decode('utf-8')
    print(data)

except Exception as e:
    print(e)
