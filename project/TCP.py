import socket
import selectors
import time
import types

class Node(object):

    def __init__(self, hostname, port=0):
        self.hostname = hostname
        self.port = port

    def start(self,o,to):
        sel = selectors.DefaultSelector()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.hostname, self.port))    #if we bind to port 0, the OS will pick an available port
            self.port = self.socket.getsockname()[1]
            self.socket.listen()
            self.socket.setblocking(False)
            sel.register(self.socket, selectors.EVENT_READ, data=None)
            try:
                while True:
                    events = sel.select(timeout=None)
                    for key, mask in events:
                        if key.data is None:
                            conn, addr = key.fileobj.accept()  # Should be ready to read
                            print(f"Accepted connection from {addr}")
                            conn.setblocking(False)
                            data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
                            events = selectors.EVENT_READ | selectors.EVENT_WRITE
                            sel.register(conn, events, data=data)
                        else:
                            sock = key.fileobj
                            data = key.data
                            if mask & selectors.EVENT_READ:
                                recv_data = sock.recv(1024)  # Should be ready to read
                                if recv_data:
                                    data.outb += recv_data
                                else:
                                    # print(f"Closing connection to {data.addr}")
                                    sel.unregister(sock)
                                    sock.close()
                            if mask & selectors.EVENT_WRITE:
                                if data.outb:
                                    # print(f"Echoing {data.outb!r} to {data.addr}")
                                    sent = sock.send(data.outb)  # Should be ready to write
                                    data.outb = data.outb[sent:]
            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            finally:
                sel.close()





            # while True:
            #     try :
            #         conn, address = self.socket.accept()
            #         with conn:
            #             data = conn.recv(2048)
            #             # ti = int(round(time.time() * 1000))
            #             # msg = str(o.id)+str(int(o.omega)*(ti-to))
            #             # self.socket.send(str.encode(msg.zfill(17)))
            #             print(data)
            #             conn.send(data)
            #     except Exception as e :
            #         conn, address = self.socket.accept()



