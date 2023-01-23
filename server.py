import socket
import threading

RESTRICTED_USERNAMES = [" System ",]

class Server():
    def __init__(self):
        self.start_server()

    def start_server(self):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        host = socket.gethostbyname(socket.gethostname())
        port = 33535

        self.clients = []

        self.s.bind((host,port))
        self.s.listen(100)

        self.username_lookup = {}

        while True:
            c, addr = self.s.accept()

            username = c.recv(10240).decode()
            if username in list(self.username_lookup.values()) or username in RESTRICTED_USERNAMES:
                c.send("System - Нou have been disconnected from the server because the same username already exists".encode())
                c.shutdown(socket.SHUT_RDWR)
                continue
            
            self.username_lookup[c] = username

            self.clients.append(c)
             
            t = threading.Thread(target=self.handle_client,args=(c,addr,))
            t.daemon=True
            t.start()
            self.broadcast(f'System - User {username} joined the chat :D')

    def broadcast(self,msg):
        for connection in self.clients:
            connection.send(msg.encode())

    def handle_client(self,c,addr):
        while True:
            try:
                msg = c.recv(9999999)
                if msg == b"LEAVE":
                    raise Exception
                elif msg == b"ONLINE":
                    users = list(self.username_lookup.values())
                    ms = "!ONLINE "
                    for m in users:
                        ms = ms + m + " "
                    c.send(ms.encode())
                    continue
            except:
                try:
                    c.shutdown(socket.SHUT_RDWR)
                    self.clients.remove(c)
                    self.broadcast(f'System - User {self.username_lookup[c]} has left the chat :(')
                    del self.username_lookup[c]
                    break
                except:
                    self.clients.remove(c)
                    self.broadcast(f'System - User {self.username_lookup[c]} has left the chat :(')
                    del self.username_lookup[c]
                    break

            if msg:
                try:
                    if ' - '.join(msg.decode('utf-8').split(" - ")[1:]).startswith("@"):
                        inv_map = {v: k for k, v in self.username_lookup.items()}
                        snd = msg.decode('utf-8').split(" - ")[0]
                        usr = ' - '.join(msg.decode('utf-8').split(" - ")[1:]).split(" ")[0][1:]
                        if usr in list(inv_map.keys()):
                            inv_map[usr].send(msg+b" [PRIVATE]")
                            inv_map[snd].send(msg+b" [PRIVATE]")
                            continue
                except:
                    pass
                for connection in self.clients:
                    connection.send(msg)

server = Server()
