# Client-Server from # https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
# Peer to peer from http://cs.berry.edu/~nhamid/p2p/framework-python.html

import socket
from datetime import datetime
from threading import Thread
from colorama import Fore
from lib.helpers import process_input, prepare_message, process_message, print_users, process_input_with_commands, process_chat_commands
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
        self.server_started = False
        self.users = dict()
        self.id = None
        self.is_server = False
        self.server_id = None

        self.color = random.choice(COLORS)

        # Connect to server and send information
        # initialize TCP socket
        self.cs = socket.socket()
        print(f"[*] Connecting to {self.SERVER_HOST}:{self.SERVER_PORT}...")
        # connect to the server
        self.cs.connect((self.SERVER_HOST, self.SERVER_PORT))

        print("[+] Connected.")
        self.client_hostname = self.cs.getsockname()[0]

        # prompt the client for a name
        self.name = input("Enter your name: ")
        print(f"Hola {self.name}, bienvenid@ al chat!")
        print(
            "Escribe un mensaje y presiona Enter para enviar. Utiliza el comando /help para",
            "mostrar la ayuda.",
            sep="\n"
        )

        self.p2p = P2P(self)
        self.port = self.p2p.port

        # inform the server our ip, port and name
        self.send(f"{self.client_hostname}-{self.port}-{self.name}")

        self.users = json.loads(self.listen())
        self.send('ping')
        self.id = self.users['self']
        del self.users['self']

        # make a thread that listens for messages to this client & print them
        t = Thread(target=self.listen_loop)
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        t.start()

    def run(self):
        while True:
            try:
                msg = input()

                if not self.server_alive:
                    break

                # Revisa si ingresó comandos y procesa la acción que corresponde
                process_chat_commands(self, msg)

            except KeyboardInterrupt:
                print("cerrando...")
                self.send("k-dead")

                self.p2p.die()

                raise KeyboardInterrupt

    def send(self, msg):
        if self.server_id is None and not self.is_server:
            try:
                self.write = self.cs.makefile('w')
                with self.write:
                    self.write.write(msg + '\n')
                    self.write.flush()
            except BrokenPipeError:
                self.server_alive = False
        elif self.is_server:
            print(msg[2:])
            self.server.msg_queue.put(msg)
        else:
            self.p2p.pm(self.server_id, msg)

    def listen(self):
        self.read = self.cs.makefile('r')
        with self.read:
            msg = self.read.readline().strip()
        return msg

    def listen_loop(self):
        while self.server_alive:
            msg = self.listen()
            if msg == "":
                print("server shutting down")
                self.server_alive = False
                break
            self.server_started = True
            id, msg = process_message(msg)

            if id == "0":
                print(msg)
            elif id == "1":
                user = msg.split(";")
                if int(self.id) != int(user[0]):
                    self.users[user[0]] = {'id': user[0],
                                           'name': user[2], 'ip': user[1]}
                print(f"¡{user[0]}: {user[2]} ha entrado a la sala!\n")
            elif id == "k":
                msg = msg.split('-')
                id = msg[0]
                msg = "-".join(msg[1:])
                del self.users[id]
                print(msg)
            elif id == "server":
                self.become_server(msg)
                # falta la recepción del estado del proceso
            elif id == "new_server":
                self.server_id = msg

    def become_server(self, msg):
        info = json.loads(msg)
        self.server = SubServer(info, self.users, self.p2p, self)
        self.is_server = True
        print("voy a ser server!!")
        self.timer = Thread(target=self.change_server)
        self.timer.daemon = True
        self.timer.start()

    def change_server(self):
        while self.is_server:
            sleep(30)
            if self.server.number_clients > 0:
                user = random.choice(list(self.users))
                self.is_server = False

                info = {}
                info['first_messages'] = self.server.first_messages
                info['number_clients'] = self.server.number_clients
                info['n_arg'] = self.server.n_arg
                info['required_clients'] = self.server.required_clients
                info['queue'] = list(self.server.msg_queue.queue)
                info['user_id'] = self.server.user_id
                info['enough_clients'] = self.server.enough_clients

                self.p2p.pm(user, "server-" + json.dumps(info))
                print(f"cambiando de server a {self.users[user]['name']}")
