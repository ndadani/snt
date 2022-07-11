import multiprocessing
from multiprocessing import shared_memory
from queue import Queue

from numpy import zeros
import TCP
import threading
import time
import json

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

    def sockets_generator(self , sock_count:int):
        for i in range(sock_count):
            server = TCP.Node(HOST,PORT)
            t = threading.Thread(target=server.start, args=())
            t.daemon = True
            threads.append(t)
            t.start()
            while server.port == 0:
                time.sleep(0.001)
            self.ports.append(server.port)
        print(self.ports)
        
def distribute(buff:memoryview , N:int):
    for i in range(1,N):
        print(i)
        k=0
        j=i-1
        while j>=0:
            print(j)
            print(k)
            buff[i].append(buff[j][k])                                                  #FIX
            k+=1
            j-=1

def core(ports_name:str , id:int , omega:int , k:int , q:Queue , o_list:list , nodes:int):
    o = Oscillator(id,omega,k,q)
    print(o_list)
    sock_count=nodes-1-len(o_list)
    print(sock_count)
    o.sockets_generator(sock_count)
    shm = shared_memory.SharedMemory(ports_name)
    shm.buf[o.id:o.id+len(o.ports)] = bytearray(o.ports)                                #FIX
    shm.buf[o.id+len(o.ports)+1:o.id+nodes] = bytearray([0]*(nodes-1-len(o.ports)))
    
    distribute(shm.buf, nodes)
    print(shm.buf)

if __name__ == "__main__":
    o_list = []
    # Initialize the nodes
    q = multiprocessing.Queue()
    nodes = int(input("> Size of the system = "))
    ports = shared_memory.SharedMemory(create=True, size=nodes)
    with open('project/data.txt','r') as f:
        for n in range(nodes):
            try :
                data = f.readline().split(',')
                process = multiprocessing.Process(target=core, args=(ports.name,n,data[0],data[1],q,o_list,nodes))
                process.daemon = True
                process.start()
                o_list.append(q.get())
                process.join()
            except Exception as e:
                print(e)

    ports.close()
    ports.unlink()  

        

