# Client-Server from # https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
# Peer to peer from http://cs.berry.edu/~nhamid/p2p/framework-python.html

import socket
from threading import Thread
from lib.helpers import (
    process_chat_commands,
)
from lib.helpers import COLORS
from lib.p2p import P2P
from lib.sub_server import SubServer
from time import sleep
import random
import json


class Client:
    def __init__(self, SERVER_HOST, SERVER_PORT):
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.server_alive = True
        self.original_server_alive = True
        self.server_started = False
        self.users = dict()
        self.id = None
        self.is_server = False
        self.server_id = None
        self.color = random.choice(COLORS)
        self.name = None

        # Connect to server and send information
        # initialize TCP socket
        self.cs = socket.socket()
        print(f"[*] Connecting to {self.SERVER_HOST}:{self.SERVER_PORT}...")
        # connect to the server
        self.cs.connect((self.SERVER_HOST, self.SERVER_PORT))

        print("[+] Connected.")
        self.client_hostname = self.cs.getsockname()[0]

        # prompt the client for a name
        # self.name = input("Enter your name: ")
        self.name = "pepe"

        print(f"Hola {self.name}, bienvenid@ al chat!")
        print(
            "Escribe un mensaje y presiona Enter para enviar. Utiliza el comando /help para",
            "mostrar la ayuda.",
            sep="\n"
        )

        self.p2p = P2P(self)
        self.port = self.p2p.port

        # inform the server our ip, port and name
        self.send({"id": "init", "hostname": f"{self.client_hostname}-{self.port}", "name": self.name})

        # Entregamos la lista de usuarios actuales al cliente y quitamos su valor en el dict
        self.users = json.loads(self.listen())
        self.send({"id": 'ping'})
        self.id = self.users['self']
        del self.users['self']

        # Entregamos la IP y el puerto del servidor inicial
        self.server_stats = self.listen()
        self.send({"id": 'ping'})

        # make a thread that listens for messages to this client & print them
        t = Thread(target=self.listen_loop)
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        t.start()

    def run(self):
        while True:
            try:
                msg = input()
                # print ('\033[1A\033[K', end="") # con esto eliminamos el input escrito y colocamos el mensaje ahí

                if not self.server_alive:
                    break

                # Revisa si ingresó comandos y procesa la acción que corresponde
                process_chat_commands(self, msg)

            except KeyboardInterrupt:
                # Revisa si el actual cliente es servidor en este momento
                if self.is_server:
                    self.change_server(closing=True)
                # Cerrar socket
                print("cerrando...")
                sleep(0.1)
                self.send({"id": "k", "msg": "dead"})

                self.p2p.die()

                raise KeyboardInterrupt

    def send(self, msg):
        if self.server_id is None and not self.is_server:
            msg = json.dumps(msg)
            try:
                self.write = self.cs.makefile('w')
                with self.write:
                    self.write.write(msg + '\n')
                    self.write.flush()
            except BrokenPipeError:
                self.server_alive = False
        elif self.is_server:
            print(msg["msg"])
            self.server.msg_queue.put(msg)
        else:
            self.p2p.pm(self.server_id, msg)

    def listen(self):
        self.read = self.cs.makefile('r')
        with self.read:
            msg = self.read.readline().strip()
        return json.loads(msg)

    def listen_loop(self):
        while self.server_alive:
            msg = self.listen()
            if msg == "":
                print("server shutting down")
                self.original_server_alive = False
                break
            self.server_started = True
            id = msg["id"]

            if id == "0":
                print(f"{msg['msg']}")
            elif id == "1":
                if int(self.id) != int(msg["user_id"]):
                    self.users[str(msg["user_id"])] = {'id': msg["user_id"],
                                           'name': msg["user_name"], 'ip': msg["user_ip"]}
                print(f"¡{msg['user_id']}: {msg['user_name']} ha entrado a la sala!\n")
            elif id == "k":
                del self.users[msg["user_id"]]
                print(f"{msg['user_name']} ha salido del chat")
            elif id == "server":
                self.become_server(msg["info"])
            elif id == "new_server":
                self.server_id = msg["client_id"]
                # Le avisamos al nuevo servidor que yo soy cliente suyo
            elif id == "original_server":
                self.server_id = None

    def become_server(self, info):
        info = json.loads(info)
        self.server = SubServer(info, self.users, self.p2p, self)
        self.is_server = True
        # self.timer = Thread(target=self.change_server)
        # self.timer.daemon = True
        # self.timer.start()

    def change_server(self, closing = False):
        while self.is_server:
            if not closing: sleep(10)

            if self.server.number_clients > 0:
                try:
                    user = random.choice(list(self.users))
                except IndexError:
                    print("no hay nadie mas conectado")
                    if closing:
                        break
                    else:
                        continue
                self.is_server = False

                info = {}
                info['first_messages'] = self.server.first_messages
                info['number_clients'] = self.server.number_clients
                info['n_arg'] = self.server.n_arg
                info['required_clients'] = self.server.required_clients
                info['queue'] = list(self.server.msg_queue.queue)
                info['user_id'] = self.server.user_id
                info['enough_clients'] = self.server.enough_clients

                self.p2p.pm(user, {"id": "server", "info": json.dumps(info)})

                del self.server
