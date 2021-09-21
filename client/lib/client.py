# Client-Server from # https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
# Peer to peer from http://cs.berry.edu/~nhamid/p2p/framework-python.html

import socket
from datetime import datetime
from threading import Thread
from colorama import Fore
from lib.helpers import process_input, prepare_message, process_message, print_users, process_input_with_commands
from lib.helpers import COLORS
from lib.p2p import P2P
from lib.commands import COMMANDS
import random
import json


class Client:
    def __init__(self, SERVER_HOST, SERVER_PORT):
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.server_alive = True
        self.users = dict()
        self.id = None

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
                self.process_chat_commands(msg)

            except KeyboardInterrupt:
                print("cerrando...")
                self.send("k-dead")

                self.p2p.die()

                raise KeyboardInterrupt


    def process_chat_commands(self, msg_input):

        command, msg = process_input_with_commands(msg_input)

        # Caso help: imprime la lista de comandos
        if command == "/help":

            for com, text in COMMANDS.items():
                print(f"  /{com:20}{text}")

        # Caso users: imprime los usuarios
        elif command == "/users":
            print(print_users(self))

        # Caso to: envía un mensaje privado
        elif command == "/to":

            # Split separa el id del destinatario y el mensaje
            msg_split = msg.split(" ", maxsplit=1)

            if len(msg_split) == 2 and msg_split[0] in self.users:
                uid = msg_split[0]
                msg = msg_split[1]

                self.p2p.pm(uid, prepare_message(self, msg, private=True))
            else:
                print("Opción no válida")

        # Caso exit: sale del chat
        elif command == "/exit":
            raise KeyboardInterrupt

        # Caso default: Si no se ingresa un comando, se envia el mensaje original a todos
        elif msg_input.strip() != "":
            self.send(prepare_message(self, msg_input))


    def send(self, msg):
        try:
            self.write = self.cs.makefile('w')
            with self.write:
                self.write.write(msg + '\n')
                self.write.flush()
        except BrokenPipeError:
            self.server_alive = False

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
                break
            id, msg = process_message(msg)

            if id == "0":
                print(msg)
            elif id == "1":
                user = msg.split(";")
                if int(self.id) != int(user[0]):
                    self.users[user[0]] = {'id': user[0], 'name': user[2], 'ip': user[1]}
                print(f"¡{user[0]}: {user[2]} ha entrado a la sala!\n")
            elif id == "k":
                msg = msg.split('-')
                id = msg[0]
                msg = "-".join(msg[1:])
                del self.users[id]
                print(msg)
