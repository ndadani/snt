import socket
import threading
import TCP

HOST = "127.0.0.1"  #local host
PORT = 0

class Oscillator(object):

    def __init__(self):
        self.id = input("> id = ")
        self.omega = input("> omega = ")
        self.k = input("> k = ")    # for now, the coupling strength depends on the oscillator, not the connection
        self.connections = []   # list of ports bound to the oscillator
        o_list.append(self)

    def sockets_generator(self, sock_count):
        for i in range(sock_count):
            server = TCP.Node(HOST,PORT)
            server.connect()
            self.connections.append(server.port)

        
if __name__ == "__main__":

    o_list=[]
    nodes = input("> Size of the system = ")
    for n in range(1,int(nodes)+1):
        o = Oscillator()
    print(o_list)

    sock_count = len(o_list)-1
    print(sock_count)
    for o in o_list:
        o.sockets_generator(sock_count)
        sock_count -= 1
        print(o.connections)

    for i in range(len(o_list)):
        for j in range(i+1,len(o_list)):
            o_list[j].connections.append(o_list[i].connections[j-i-1])
        print(o_list[i].connections)

        


