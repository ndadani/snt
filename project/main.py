import multiprocessing
from queue import Queue
import socket
import sys
import selectors
import types
import numpy
import TCP
import threading
import time

HOST = "127.0.0.1"  #local host
PORT = 0
LOOP = 1
BUF_SIZE = 1024
threads=[]

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

def which_osc(ports_list:list, N:int):
    osc = []
    for p in range(len(ports_list)):
        index_pos_list = []
        for i in range(len(ports_list)):
            if i!=p and ports_list[i] == ports_list[p]:
                index_pos_list.append(i)
        for j in index_pos_list:
            osc.append(j//(N-1))
    return osc


class Oscillator(object):

    def __init__(self , id:int , omega:int , k:int , ports:list, q:Queue):
        self.id = id
        self.omega = omega
        self.k = k    # for now, the coupling strength depends on the oscillator, not the connection
        self.ports = ports   # list of ports bound to the oscillator
        self.evolution = []
        q.put(self)

    def sockets_generator(self , sock_count:int, nodes:int, q_info:Queue, which_osc:list):
        for i in range(sock_count):
            print(self.id , "<<<")
            server = TCP.Node(HOST,self.ports[i])
            t = threading.Thread(target=server.start, args=(self,to,q_info,which_osc[i]))
            t.daemon = True
            t.start()
            # threads.append(t)

    def threaded_connection(self, port:int , to:int, q_info:Queue, which_osc:int):
        ti = int(round(time.time() * 1000))
        msg = str.encode("S"+str(self.omega)+"/"+str(ti-to)+"E*")
        self.evolution.append(msg)
        messages = [msg for i in range(0,LOOP)]
        sel = selectors.DefaultSelector()
        # conn_count=1
        # for i in range(0, conn_count):
        #     connid = i+1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:   #TCP
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setblocking(False)
            s.connect_ex((HOST, port))
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            # for x in range(5):
            data = types.SimpleNamespace(
                # connid=connid,
                msg_total=sum(len(m) for m in messages),
                recv_total=0,
                messages=messages.copy(),
                outb=b"",
            )
            sel.register(s, events, data=data)
            try:
                while True:
                    events = sel.select(timeout=None)
                    for key, mask in events:
                        if key.data is None:
                            conn, addr = key.fileobj.accept()  # Should be ready to read
                            # print(f"Accepted connection from {addr}")
                            conn.setblocking(False)
                            data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
                            events = selectors.EVENT_READ | selectors.EVENT_WRITE
                            sel.register(conn, events, data=data)
                        else:
                            sock = key.fileobj
                            data = key.data
                            if mask & selectors.EVENT_READ:
                                recv_data = sock.recv(BUF_SIZE)  # Should be ready to read
                                if recv_data:
                                    # print(f"\033[92m{self.id} : Received {recv_data!r} from {which_osc} on port {port}\033[0m")
                                    # print("———recv_data———"+str(sys.getsizeof(recv_data)))
                                    q_info.put(which_osc)
                                    q_info.put(recv_data)
                                    data.recv_total += len(recv_data)
                                if not recv_data or data.recv_total == data.msg_total:
                                    # print(f"Closing connection {data.connid}")
                                    sel.unregister(sock)
                                    sock.close()
                            if mask & selectors.EVENT_WRITE:
                                if not data.outb and data.messages:
                                    # data.outb = data.messages.pop(0)
                                    data.outb = data.messages.pop(0)
                                    # data.outb = str.encode("S"+str(self.omega)+"/"+str(ti-to)+"E*")
                                if data.outb:
                                    print(f"\033[31m{self.id} : Sending {data.outb!r} to {which_osc} on port {port}\033[0m")
                                    sent = sock.send(data.outb)  # Should be ready to write
                                    data.outb = data.outb[sent:]
                                    # print(sent)
            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            finally:
                sel.close()

        



def replica(ports_list:list, id:int , omega:int , k:int , q:Queue , o_list:list , nodes:int, to:int, which_osc:list):
    o = Oscillator(id,omega,k,ports_list,q)
    sock_count=nodes-1-len(o_list)
    # print(sock_count)
    q_info = Queue()
    o.sockets_generator(sock_count, nodes, q_info, which_osc)
    for i in range(len(o.ports)-sock_count-1,-1,-1):
        print(">>>" , o.id)
        t = threading.Thread(target=o.threaded_connection, args=(o.ports[i],to,q_info,which_osc[i]))
        t.daemon = True
        t.start()
        # t.join()
        # threads.append(t)

    time.sleep(2)
    # while not q_info.empty():
    #     print(q_info.get())

    # for t in threads:
    #     t.join()




    
if __name__ == "__main__":
    to = int(round(time.time() * 1000))
    # IPC
    q = Queue()
    o_list = []
    # Initialize the nodes
    nodes = int(input("> Size of the system = "))
    ports_list = [0]*nodes*(nodes-1)
    for i in range(nodes):
        sock_count=nodes-1-i
        for j in range(sock_count):
            socky = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socky.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
            socky.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socky.bind((HOST, 0))  # get any available port
            port = socky.getsockname()[1]
            ports_list[i*(nodes-1)+j] = port
            socky.close()
    # print(ports_list)
    distribute(ports_list, nodes)
    print(ports_list)
    # print(which_osc(ports_list,nodes))
    osc = which_osc(ports_list,nodes)

    with open('project/data.txt','r') as f:
        for n in range(nodes):
            try :
                data = f.readline().split(',')
                # process = multiprocessing.Process(target=replica, args=(shared_list,n,data[0],data[1],q,o_list,nodes))
                t = threading.Thread(target=replica, args=(ports_list[n*(nodes-1):n*(nodes-1)+nodes-1],n,data[0],data[1],q,o_list,nodes,to,osc[n*(nodes-1):n*(nodes-1)+nodes-1]))     # pour l'instant
                threads.append(t)
                t.daemon = True
                t.start()
                o_list.append(q.get())
            except Exception as e:
                print(e)
    # print(len(threads))
    for t in threads:
        t.join()

        












