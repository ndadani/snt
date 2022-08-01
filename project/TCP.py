import socket
import selectors
import time
import types

class Node(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def start(self,o,to,q,osc):
        # print("HEY")
        sel = selectors.DefaultSelector()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.hostname, self.port))
            self.port = self.socket.getsockname()[1]
            self.socket.listen()
            self.socket.setblocking(False)
            sel.register(self.socket, selectors.EVENT_READ, data=None)
            try:
                while True:
                    events = sel.select(timeout=None)
                    for key, mask in events:
                        if key.data is None:
                            conn, addr = key.fileobj.accept()
                            # print(f"Accepted connection from {addr}")
                            conn.setblocking(False)
                            data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
                            events = selectors.EVENT_READ | selectors.EVENT_WRITE
                            sel.register(conn, events, data=data)
                        else:
                            sock = key.fileobj
                            data = key.data
                            if mask & selectors.EVENT_READ:
                                recv_data = sock.recv(1024)
                                if recv_data:
                                    # print(f"\033[92m{self.port} : Received {recv_data!r} from {o.id}\033[0m")
                                    aux=recv_data.split(b"*")
                                    # print(aux)
                                    for x in aux:
                                        if x:
                                            # print(x)
                                            data.outb += x
                                else:
                                    # print(f"Closing connection to {data.addr}")
                                    sel.unregister(sock)
                                    sock.close()
                            if mask & selectors.EVENT_WRITE:
                                if data.outb:
                                    # print(f"Echoing {data.outb!r} to {data.addr}")
                                    print(f"\033[92m{o.id} : Sending {data.outb!r} to {osc} on port {self.port}\033[0m")
                                    sent = sock.send(data.outb)
                                    data.outb = data.outb[sent:]
            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            finally:
                sel.close()




