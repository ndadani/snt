from datetime import datetime
import os
import socket
import selectors
import time
import types

LOOP = 1

class Node(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def start(self,o,to,q,osc,signal):

        # ti = int(round(time.time() * 1000))
        now = datetime.now()
        ti = datetime.timestamp(now)
        msg = str.encode("S"+str(osc)+'/'+str(o.id)+'/'+str(o.omega)+"/"+str(ti-to)+"E")
        o.evolution[ti-to] = o.omega
        messages = [msg for i in range(0,LOOP)]
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
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
                    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
                    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.socket.setblocking(False)
                    self.socket.bind((self.hostname, self.port))
                    self.socket.listen()

                    events = selectors.EVENT_READ | selectors.EVENT_WRITE
                    sel.register(self.socket, events, data=None)

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
                                        recv_data = sock.recv(1024)
                                        if recv_data:
                                            print(f"\033[92m{o.id} : Received {recv_data!r} from {osc} on port {self.port}\033[0m")
                                            aux = recv_data.decode()
                                            aux = aux.strip('ES')
                                            # print(aux)
                                            l = aux.split('/',1)
                                            # print(l)
                                            if l[0]==str(o.id):
                                                q.put(l[1])
                                            data.recv_total += 1
                                            signal.set()
                                        if not recv_data or data.recv_total == data.msg_total:
                                            # print(f"Closing connection of {o.id} to {osc}")
                                            sel.unregister(sock)
                                            sock.close()
                                    if mask & selectors.EVENT_WRITE:
                                        if not data.outb and data.messages:
                                            data.outb = data.messages.pop(0)
                                        if data.outb:
                                            print(f"\033[31m{o.id} : Sending {data.outb!r} to {osc} on port {self.port}\033[0m")
                                            sent = sock.send(data.outb)
                                            data.outb = data.outb[sent:]
                    except KeyboardInterrupt:
                        print("Caught keyboard interrupt, exiting")
                    finally:
                        sel.close()
            except:
                pass




