import socket
import threading
import time
import TCP

HOST = "127.0.0.1"  #local host
PORT = 0

class Oscillator(object):

    def __init__(self):
        self.id = input("> id = ")
        self.omega = input("> omega = ")
        self.k = input("> k = ")    # for now, the coupling strength depends on the oscillator, not the connection
        self.ports = []   # list of ports bound to the oscillator
        o_list.append(self)

    def sockets_generator(self, sock_count):
        for i in range(sock_count):
            server = TCP.Node(HOST,PORT)
            t = threading.Thread(target=server.start, args=())
            t.daemon = True
            threads.append(t)
            t.start()
            while server.port == 0:
                time.sleep(0.001)
            self.ports.append(server.port)

    def connect_to_port(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

    def threaded_connection(self, port):
        t = threading.Thread(target=self.connect_to_port, args=(HOST,port))
        t.daemon = True
        threads.append(t)
        #t.start()
 
if __name__ == "__main__":

    threads = []

    # Initialize the nodes
    o_list=[]
    nodes = input("> Size of the system = ")
    for n in range(1,int(nodes)+1):
        o = Oscillator()

    # Create Sockets bound to different ports on multiple threads
    sock_count = len(o_list)-1
    for o in o_list:
        o.sockets_generator(sock_count)
        sock_count -= 1
        print(o.ports)
    

    # Distribute the ports and connect the oscillator
    for i in range(len(o_list)):
        for j in range(i+1,len(o_list)):
            o_list[j].ports.append(o_list[i].ports[j-i-1])
            o.threaded_connection(o_list[i].ports[j-i-1])
        print(o_list[i].ports)


        


