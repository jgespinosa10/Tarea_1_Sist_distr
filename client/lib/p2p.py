from threading import Thread
from lib.helpers import process_ip
from colorama import Fore
import socket
import json


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
        return self.user.users.get(id, None)

    def send(self, skt, msg):
        msg = json.dumps(msg)
        write = skt.makefile('w')
        with write:
            write.write(msg + '\n')
            write.flush()

    def listen(self, skt):
        read = skt.makefile('r')
        with read:
            msg = read.readline().strip()
        return json.loads(msg)

    def listen_loop(self, skt):
        try:
            msg = self.listen(skt)
            msg = json.loads(msg)
            if msg == "":
                skt.close()
                return

            id = msg["id"]
            if id == "new_server":
                self.user.server_id = msg["msg"]
            elif id == "server":
                self.user.become_server(msg["msg"])
            elif id == "0" and self.user.is_server:
                print(msg["msg"])
                self.user.server.msg_queue.put({"id": id, "msg": msg["msg"]})
            elif id == "0" or id == "p":
                print(msg["msg"])

        except ConnectionResetError:
            skt.close()
            return

        skt.close()
        return

    def pm(self, id, old_msg):
        msg = old_msg["msg"]
        skt = socket.socket()
        peer = self.peer(id)
        if not peer: return
        skt.connect(process_ip(peer['ip']))
        peer['socket'] = skt
        print(old_msg["msg"])

        self.send(skt, str(self.user.id))
        self.listen(skt)
        self.send(peer['socket'], json.dumps(old_msg))

    def die(self):
        for _, info in self.user.users.items():
            if 'socket' in info:
                info['socket'].close()
