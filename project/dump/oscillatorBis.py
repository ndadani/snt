import multiprocessing
from operator import mul
import threading
import socket
import time
import numpy
import TCP

HOST = "127.0.0.1"  #local host
PORT = 0
threads = []
o_list=[]

class Oscillator(object):

    # Server like oscillator
    def __init__(self):
        self.id = input("> id = ")
        self.omega = input("> omega = ")
        self.k = input("> k = ")    # for now, the coupling strength depends on the oscillator, not the connection
        self.ports = []   # list of ports bound to the oscillator
        o_list.append(self)

    def sockets_generator(self,sock_count):
        for i in range(sock_count):
            server = TCP.Node(HOST,PORT)
            t = threading.Thread(target=server.start, args=())
            t.daemon = True
            threads.append(t)
            t.start()
            while server.port == 0:
                time.sleep(0.001)
            self.ports.append(server.port)

    # Client like oscillator
    def connect_to_port(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        
    def threaded_connection(self, port):
        t = threading.Thread(target=self.connect_to_port, args=(HOST,port))
        t.daemon = True
        threads.append(t)
        t.start()

    # Core of the process
    # def core(self, o_list):
    #     try:
    #         for o in o_list:
    #             for port in o.ports:
    #                 p = multiprocessing.Process(target=o.threaded_connection, args=(port,))
    #                 p.daemon = True
    #                 p.start()
    #             for process in multiprocessing.active_children():
    #                 p.join()
    #     except Exception as e:
    #         print(e)
            
if __name__ == "__main__":
    # Initialize the nodes
    nodes = input("> Size of the system = ")
    print("Initialize the oscillators")
    for n in range(1,int(nodes)+1):
        process = multiprocessing.Process(target=Oscillator)
        process.daemon = True
        process.start()
    for process in multiprocessing.active_children():
        process.join()
    
    # Create Sockets bound to different ports on multiple threads
    sock_count = len(o_list)-1
    print(sock_count)
    for o in o_list:
        o.sockets_generator(sock_count)
        sock_count -= 1
        
    # Distribute the ports and connect the oscillator
    for i in range(len(o_list)):
        for j in range(i+1,len(o_list)):
            o_list[j].ports.append(o_list[i].ports[j-i-1])
            o.threaded_connection(o_list[i].ports[j-i-1])
        print("Oscillator "+o_list[i].id+" is connected to port: ") 
        print(o_list[i].ports)


    
    


