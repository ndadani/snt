import socket
import numpy

HOST = "127.0.0.1"  # localhost
PORT = 9001  # The port used by the server

id = input("> id = ")
omega = input("> omega = ")
k = input("> k = ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #TCP

try:
    s.connect((HOST, PORT))
    s.sendall(str.encode(id+':'+omega+':'+k))
    print(str.encode(id+':'+omega+':'+k))
    osci_list=dict()
    while True:
        data = s.recv(2048).decode('utf-8')
        if data == 'NOW':
            break
        data = data.split(':')
        osci_list[data[0]] = float(data[2]) * numpy.sin((float(omega) - float(data[1]))*numpy.pi/180)
    for o in osci_list.values():
        aux = float(omega) + o
        omega = str(aux)
    print(omega)
    s.sendall(str.encode(id+':'+str(omega)+':'+k))
    s.close()

except Exception as e:
    print(e)




# #TODO wait/get results from other threads (PORT, QUEUE, .. ?)
# #TODO Format data size, struct.error: unpack requires a buffer of 4 bytes
# #TODO BrokenPipeError: [Errno 32] Broken pipe
# #TODO ConnectionResetError: [Errno 54] Connection reset by peer
# #TODO include ids to change data

# import socket
# import numpy
# import struct
# import threading

# HOST = "127.0.0.1"  # localhost
# PORT = 9001  # The port used by the server

# def oscillator(ip, port, omega, k, id):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #TCP
#     try:
#         s.connect((ip, port))
#         omega = float(omega)
#         send = struct.pack('f',omega)
#         #send += b"0" * (4 - len(send))
#         #print(send)
#         s.sendall(send)
#         data = struct.unpack('f',s.recv(1024))
#         print(data)
#         dphi = omega + float(k) * numpy.sin((omega - data[0])*numpy.pi/180)
#         print(dphi)
#         s.sendall(dphi)
#         s.close()
#     except Exception as e:
#         print(e)

# if __name__ == "__main__":
#     thread_list = dict()
#     SOCKET_AMOUNT = input("> Number of oscillators = ")
#     for i in range(1,int(SOCKET_AMOUNT)+1):
#         id = input("> id = ")
#         omega = input("> omega = ")
#         k = input("> k = ")
#         client_thread = threading.Thread(target=oscillator, args=(HOST, PORT, omega, k, id))
#         client_thread.setDaemon(True)
#         thread_list[id]=client_thread
#     for c in thread_list.values():
#         c.start()

#     msg = input()
#     if msg=="":
#         [x.join() for x in thread_list.values()]

#     # elif msg in thread_list.keys():
#     #     [x.join() for x in thread_list.values()]
#     #     omega = input("> omega = ")
#     #     k = input("> k = ")
#     #     client_thread = threading.Thread(target=oscillator, args=(HOST, PORT, omega, k, msg))
#     #     client_thread.setDaemon(True)
#     #     thread_list[msg]=client_thread
#     #     client_thread.start()
    






    

    


