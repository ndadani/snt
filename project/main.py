import multiprocessing
from queue import Queue

import numpy
import TCP
import threading
import time

HOST = "127.0.0.1"  #local host
PORT = 0
threads = []

class Oscillator(object):

    def __init__(self , id:int , omega:int , k:int , q:Queue):
        self.id = id
        self.omega = omega
        self.k = k    # for now, the coupling strength depends on the oscillator, not the connection
        self.ports = []   # list of ports bound to the oscillator
        q.put(self)

    def sockets_generator(self , sock_count:int, nodes:int):
        for i in range(sock_count):
            server = TCP.Node(HOST,PORT)
            t = threading.Thread(target=server.start, args=())
            t.daemon = True
            threads.append(t)
            t.start()
            while server.port == 0:
                time.sleep(0.001)
            self.ports.append(server.port)
        self.ports = self.ports + [0]*(nodes-1-sock_count)
        # print(self.ports)
        
def distribute(l:list , N:int):
    k=0
    for i in range(N-1,0,-1):
        j=0
        h=N-1-i
        k=N-1-i
        while j<i:
            l[i*(N-1)+h]=l[j*(N-1)+k]
            h+=1
            j+=1

def threaded_connection(host, port):



def replica(ports_list:list, id:int , omega:int , k:int , q:Queue , o_list:list , nodes:int):
    o = Oscillator(id,omega,k,q)
    sock_count=nodes-1-len(o_list)
    o.sockets_generator(sock_count, nodes)
    ports_list.extend(o.ports)
    if len(ports_list)==nodes*(nodes-1) :
        distribute(ports_list, nodes)


if __name__ == "__main__":
    o_list = []
    # Initialize the nodes
    q = multiprocessing.Queue()
    nodes = int(input("> Size of the system = "))
    manager = multiprocessing.Manager()
    shared_list = manager.list()
    with open('project/data.txt','r') as f:
        for n in range(nodes):
            try :
                data = f.readline().split(',')
                process = multiprocessing.Process(target=replica, args=(shared_list,n,data[0],data[1],q,o_list,nodes))
                process.daemon = True
                process.start()
                o_list.append(q.get())
                process.join()
            except Exception as e:
                print(e)

        