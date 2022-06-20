import socket
import numpy

def oscillator(omega, k):
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    s.sendall(bytes(omega))

    data = s.recv(1024)
    print(f"Received {data!r}")
    dphi = omega + k * numpy.sin((omega - int.from_bytes(data,"little"))*numpy.pi/180)
    print(dphi)
    s.sendall(dphi)
    s.close()

if __name__ == '__main__': 
    # for i in range(10):
    #     print(i)
    #     oscillator(i*10,i)
    oscillator(10,5)





































# from threading import Thread
# import socket

# def main(id,omega,connected_oscill_ids):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       #TCP protocol
#     # new_thread = Thread(target=s.recv,args=(id,))
#     # new_thread.start()
#     # new_thread.join()
#     s.connect(('localhost',9999))
    
#     while True:
#         data = s.recv(1024).decode()
#         if not data:
#             break
#         message_id, message = data.split(":", 1)
#         if message_id in connected_oscill_ids:
#             msg += message
#     phi =lambda t: omega*t + msg
#     s.send('{}:{}'.format(id,phi))

# if  __name__  == "__main__":
#     main(1,20,(2,3))

# import socket
# client_object = socket.socket()
# # This is another example of declaring a socket here by default
# # AF_INET and SOCK_STREAM gets selected
# client_object.connect(('localhost',9999))
# # Same as that for a Server.
# # The packet are generally utf-8 coded hence to decode use decode () method.
# print(client_object.recv(1024).decode())
# client_object.send (bytes ("Data transfer successful...", 'utf-8'))
# client_object.close()