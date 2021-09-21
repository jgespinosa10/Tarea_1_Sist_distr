from threading import Thread
from lib.helpers import process_ip
from colorama import Fore
import socket


class P2P:
    def __init__(self, user):
        self.user = user
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('', 0))
        self.s.listen()
        self.port = self.s.getsockname()[1]

        t = Thread(target=self.accept_peers_loop)
        t.daemon = True
        t.start()

    def accept_peers_loop(self):
        while True:
            skt, address = self.s.accept()
            id = self.listen(skt)
            self.peer(id)['socket'] = skt

            t = Thread(target=self.listen_loop, args=(skt,))
            t.deamon = True
            t.start()

            self.send(skt, 'ping')

    def peer(self, id):
        return self.user.users[id]

    def send(self, skt, msg):
        write = skt.makefile('w')
        with write:
            write.write(msg + '\n')
            write.flush()

    def listen(self, skt):
        read = skt.makefile('r')
        with read:
            msg = read.readline().strip()
        return msg

    def listen_loop(self, skt):
        while True:
            try:
                msg = self.listen(skt)
                if msg == "":
                    skt.close()
                    break
                msg = msg.split('-')
                msg = "-".join(msg[1:])
                print(msg)
            except ConnectionResetError:
                break

    def pm(self, id, msg):
        if 'socket' not in self.peer(id):
            skt = socket.socket()
            skt.connect(process_ip(self.peer(id)['ip']))
            self.peer(id)['socket'] = skt

            self.send(skt, str(self.user.id))
            self.listen(skt)

            t = Thread(target=self.listen_loop, args=(skt,))
            t.deamon = True
            t.start()

        self.send(self.peer(id)['socket'], msg)

    def die(self):
        for id, info in self.user.users.items():
            if 'socket' in info:
                info['socket'].close()
