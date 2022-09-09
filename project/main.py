from datetime import datetime
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
LOOP = 1
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

    def __init__(self , id:int , omega:int , ports:list, q:Queue):
        self.id = id
        self.omega = omega
        self.k = dict()
        self.ports = ports
        self.evolution = dict()
        self.history = dict()
        q.put(self)

    def sockets_generator(self , sock_count:int, q_info:Queue, which_osc:list, signal:list):
        for i in range(sock_count):
            # print("\033[92mServer >>>\033[0m", self.id)
            server = TCP.Node(HOST,self.ports[i])
            t = threading.Thread(target=server.start, args=(self,to,q_info,which_osc[i],signal[i]))
            t.daemon = True
            t.start()
            # threads.append(t)

    def threaded_connection(self, port:int , to:int, q_info:Queue, which_osc:int, signal:threading.Event):
        # ti = int(round(time.time() * 1000))
        now = datetime.now()
        ti = datetime.timestamp(now)
        msg = str.encode("S"+str(which_osc)+'/'+str(self.id)+'/'+str(self.omega)+"/"+str(ti-to)+"E")
        self.evolution[ti-to] = self.omega
        messages = [msg]
        data = types.SimpleNamespace(
            # msg_total=sum(len(m) for m in messages),
            msg_total=LOOP,
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )

        sel = selectors.DefaultSelector()
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.setblocking(False)
                    s.connect_ex((HOST, port))

                    events = selectors.EVENT_READ | selectors.EVENT_WRITE
                    sel.register(s, events, data=data)

                    try:
                        while True:
                            events = sel.select(timeout=None)
                            for key, mask in events:
                                if key.data is None:
                                    conn, addr = key.fileobj.accept()
                                    conn.setblocking(False)
                                    events = selectors.EVENT_READ | selectors.EVENT_WRITE
                                    sel.register(conn, events, data=data)
                                else:
                                    sock = key.fileobj
                                    data = key.data
                                    if mask & selectors.EVENT_READ:
                                        recv_data = sock.recv(2048)
                                        if recv_data:
                                            print(f"\033[92m{self.id} : Received {recv_data!r} from {which_osc} on port {port}\033[0m")
                                            aux = recv_data.decode()
                                            aux = aux.strip('ES')
                                            # print(aux)
                                            l = aux.split('/',1)
                                            # print(l)
                                            if l[0]==str(self.id):
                                                q_info.put(l[1])
                                            # data.recv_total += len(recv_data)
                                            data.recv_total += 1
                                            signal.set()
                                        if not recv_data or data.recv_total == data.msg_total:
                                            # print(f"Closing connection of {self.id} to {which_osc}")
                                            sel.unregister(sock)
                                            sock.close()
                                    if mask & selectors.EVENT_WRITE:
                                        if not data.outb and data.messages:
                                            data.outb = data.messages.pop(0)
                                        if data.outb:
                                            print(f"\033[31m{self.id} : Sending {data.outb!r} to {which_osc} on port {port}\033[0m")
                                            sent = sock.send(data.outb)
                                            data.outb = data.outb[sent:]
                    except KeyboardInterrupt:
                        print("Caught keyboard interrupt, exiting")
                    finally:
                        sel.close()
            except:
                pass
            



def replica(ports_list:list, id:int , omega:int , q:Queue , o_list:list , nodes:int, to:int, which_osc:list):
    o = Oscillator(id,omega,ports_list,q)
    sock_count=nodes-1-len(o_list)
    q_info = Queue()
    event = threading.Event()
    signalS = [threading.Event() for i in range(sock_count)]
    signalC = [threading.Event() for i in range(len(o.ports)-sock_count)]
    # print(signalS,signalC)

    o.sockets_generator(sock_count, q_info, which_osc, signalS)

    for i in range(len(o.ports)-sock_count-1,-1,-1):
        # print("\033[31mClient >>>\033[0m" , o.id)
        t = threading.Thread(target=o.threaded_connection, args=(o.ports[i],to,q_info,which_osc[i], signalC[i]))
        t.daemon = True
        t.start()
        # t.join()
        # threads.append(t)

    # count = 0
    # while True:
    #     count = 0
    #     for e in signalS+signalC:
    #         if e.is_set():
    #             count+=1
    #     if count==nodes-1:
    #         event.set()

    # event.wait(nodes)

    time.sleep(nodes)
    # for e in signalC+signalS:
    #     print(e.is_set())
    l = []
    while not q_info.empty():
        l.append(q_info.get())
    print(o.id , l)

    # for t in threads:
    #     t.join()

if __name__ == "__main__":
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

    print(ports_list)
    distribute(ports_list, nodes)
    print(ports_list)
    osc = which_osc(ports_list,nodes)
    print(osc)

    # to = int(round(time.time() * 1000))
    now = datetime.now()
    to = datetime.timestamp(now)
    # IPC
    q = Queue()
    o_list = []

    with open('project/data.txt','r') as f:
        for n in range(nodes):
            try :
                data = f.readline().split(',')
                t = threading.Thread(target=replica, args=(ports_list[n*(nodes-1):n*(nodes-1)+nodes-1],n,data[0],q,o_list,nodes,to,osc[n*(nodes-1):n*(nodes-1)+nodes-1]))
                threads.append(t)
                t.daemon = True
                t.start()
                o_list.append(q.get())
            except Exception as e:
                print(e)
    for t in threads:
        t.join()

        


