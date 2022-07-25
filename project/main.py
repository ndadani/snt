import io
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
LOOP = 2
BUF_SIZE = 1024


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
            t = threading.Thread(target=server.start, args=(self,to))
            t.daemon = True
            t.start()
            while server.port == 0:
                time.sleep(0.001)
            self.ports.append(server.port)
        self.ports = self.ports + [0]*(nodes-1-sock_count)
        # print(self.ports)


    def threaded_connection(self,port,to):
        ti = int(round(time.time() * 1000))
        # msg = str(int(self.omega)*(ti-to))
        messages = [str.encode(str(i*10)) for i in range(0,LOOP)]
        sel = selectors.DefaultSelector()
        conn_count=1
        for i in range(0, conn_count):
            connid = i+1
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:   #TCP
                s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setblocking(False)
                s.connect_ex((HOST, port))
                events = selectors.EVENT_READ | selectors.EVENT_WRITE
                data = types.SimpleNamespace(
                    connid=connid,
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
                                    recv_data = sock.recv(16)  # Should be ready to read
                                    print(str(BUF_SIZE)+"—————————BUF_SIZE")
                                    if recv_data:
                                        print(f"{key.fd} : Received {recv_data!r}")
                                        print("———recv_data———"+str(sys.getsizeof(recv_data)))
                                        data.recv_total += len(recv_data)
                                    if not recv_data or data.recv_total == data.msg_total:
                                        # print(f"Closing connection {data.connid}")
                                        sel.unregister(sock)
                                        sock.close()
                                if mask & selectors.EVENT_WRITE:
                                    if not data.outb and data.messages:
                                        data.outb = data.messages.pop(0)
                                    if data.outb:
                                        print(f"{key.fd} : Sending {data.outb!r}")
                                        BUF_SIZE=sys.getsizeof(data.outb)
                                        print("———data.outb———"+str(sys.getsizeof(data.outb)))
                                        sent = sock.send(data.outb)  # Should be ready to write
                                        data.outb = data.outb[sent:]
                except KeyboardInterrupt:
                    print("Caught keyboard interrupt, exiting")
                finally:
                    sel.close()

                # while signal:
                #     try:
                #         ti = int(round(time.time() * 1000))
                #         msg = "S"+str(self.id)+":"+str(int(self.omega)*(ti-to))+"E"
                #         count = 1
                #         # while sys.getsizeof(msg)!= 64:
                #         #     msg = msg.zfill(len(msg)+count)
                #         #     count+=1
                        
                #         # print(sys.getsizeof(msg))
                #         s.sendall(str.encode(msg))
                #         data = s.recv(2048)
                #         print(data.decode()+str(threading.get_ident()))
                #     except Exception as e:
                #         print("You have been disconnected from the server")
                #         print(e)
                #         signal = False
                #         break
        
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


def replica(ports_list:list, id:int , omega:int , k:int , q:Queue , o_list:list , nodes:int, to:int):
    o = Oscillator(id,omega,k,q)
    sock_count=nodes-1-len(o_list)
    o.sockets_generator(sock_count, nodes)
    ports_list.extend(o.ports)

    if len(ports_list)==nodes*(nodes-1) :  #c'est pas ce qu'il faut faire mais ça marche pour l'instant
        distribute(ports_list, nodes)
    # print(ports_list)
    # while len(ports_list)!= nodes*(nodes-1) and ports_list[-1]==0 :
    #     wait

    for port in ports_list[o.id:o.id+nodes-1]:
            t = threading.Thread(target=o.threaded_connection, args=(port,to))
            t.daemon = True
            t.start()
    
if __name__ == "__main__":
    to = int(round(time.time() * 1000))
    # IPC
    q = multiprocessing.Queue()
    o_list = []
    manager = multiprocessing.Manager()
    shared_list = manager.list()
    # Initialize the nodes
    nodes = int(input("> Size of the system = "))
    with open('project/data.txt','r') as f:
        for n in range(nodes):
            try :
                data = f.readline().split(',')
                # process = multiprocessing.Process(target=replica, args=(shared_list,n,data[0],data[1],q,o_list,nodes))
                t = threading.Thread(target=replica, args=(shared_list,n,data[0],data[1],q,o_list,nodes,to))     # pour l'instant
                t.daemon = True
                t.start()
                o_list.append(q.get())
                t.join()
            except Exception as e:
                print(e)

        