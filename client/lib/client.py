# Client-Server from # https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
# Peer to peer from http://cs.berry.edu/~nhamid/p2p/framework-python.html

import random
import socket
from colorama import init, Fore
from datetime import datetime
from threading import Thread

from lib.helpers import makeserversocket, process_ip

# Separators of id's: ":"

class Client:
    def __init__(self, SERVER_HOST, SERVER_PORT, separator_token):
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.separator_token = separator_token
        # init colors
        init()
        # set the available colors
        colors = [
            Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
            Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
            Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
            Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
        ]
        # choose a random color for the client
        self.client_color = random.choice(colors)

        ## Prepare client for p2p connection
        # init variables
        self.client_sockets = set()
        # create server socket
        self.ss = makeserversocket(self)
        self.client_port = self.ss.getsockname()[1]
        # make a thread that listens for messages to this client & print them
        t = Thread(target=self.accept_private_sockets)
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        # start the thread
        t.start()

        # Connect to server and send information
        # initialize TCP socket
        self.cs = socket.socket()
        print(f"[*] Connecting to {self.SERVER_HOST}:{self.SERVER_PORT}...")
        # connect to the server
        self.cs.connect((self.SERVER_HOST, self.SERVER_PORT))
        print("[+] Connected.")
        self.client_hostname = self.cs.getsockname()[0]


        # inform the server client's ip address
        self.cs.send(f"{self.client_hostname}-{self.client_port}".encode())

        # prompt the client for a name
        self.name = input("Enter your name: ")
        print(f"{self.client_color}Hola {self.name}, bienvenid@ al chat!{Fore.RESET}")
        self.cs.send(self.name.encode())

        #recieve list of id's
        try:
            message = self.cs.recv(1024).decode()
            self.users_sockets ={}
            self.users_ip = {}
            self.users = [msg.split(",") for msg in message[1:].split(";")]
            if not self.users[0][0]:
                self.users = dict()
                self.users_ip = {}
            else:
                # We obtain (ip, port) for each user
                self.users_ip = {msg[0]: process_ip(msg[1]) for msg in self.users}
                self.users = {msg[0]: msg[2] for msg in self.users}
                
        except Exception as e:
            print(e)

            # Se ejecuta cuando se sale del chat y cuando el servidor termina antes que el cliente
            return
        # make a thread that listens for messages to this client & print them
        t = Thread(target=self.listen_for_messages)
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        # start the thread
        t.start()

    ## Functions for client-server main chat
    # Function excuted in thread, listen information from server
    def listen_for_messages(self):
        while True:
            try:
                message = self.cs.recv(1024).decode()
                msg = message.split("-")
                id = msg[0]
                msg = "-".join(msg[1:])
                if id == "0":
                    print(msg, end="")
                elif id == "1":
                    user = msg.split(";")
                    self.users[user[0]] = user[2]
                    self.users_ip[user[0]] = process_ip(user[1])
                    print(f"¡{user[0]}: {user[2]} ha entrado a la sala!\n")
            # Se ejecuta cuando se sale del chat y cuando el servidor termina antes que el cliente
            except Exception:
                break

    def print_users(self):
        text= ""
        for id, name in self.users.items():
            text += f" {id}. - {name}\n"
        return text
    
    def process_message(self, msg):
        msg = msg.split(":")
        id = msg[0]
        msg = ":".join(msg[1:])
        return id, msg

    def run(self):
        while True:
            # input message we want to send to the server
            msg =  input("".join([
                "Menú:\n",
                "-1. Salir del chat\n",
                " 0. Enviar a todos\n",
                self.print_users(),
                "Escribe de la siguiente forma: {id}: {mensaje}\n"
            ]))
            # a way to exit the program
            id, msg = self.process_message(msg)
            if id == '-1':
                break
            elif id == '0':
                # add the datetime, name & the color of the sender
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                metadata = f"0-{self.client_color}[{date_now}] {self.name}{self.separator_token}" 
                to_send = f"{metadata}{msg}{Fore.RESET}"
                # finally, send the message
                self.cs.send(to_send.encode())
            elif id.isnumeric() and id in self.users:
                # stablish p2p connection and send message
                if id not in self.users_sockets:
                    # send msg through socket
                    skt = socket.socket()
                    skt.connect(self.users_ip[id])
                    self.users_sockets[id] = skt
                self.users_sockets[id].send(f"0:{msg}".encode())
            else:
                print("Elige un id válido")

        # close the socket
        self.cs.close()

    
    ## Funtions for peer 2 peer
    # Creates a socket for the client to listen to another clients
    def listen(self, user):
        try:
            # keep listening for a message from `cs` socket
            msg = user.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"{Fore.RED}[!] Error: {e}{Fore.RESET}")
            self.client_sockets.remove(user)
            user.close()
            for client in self.client_sockets:
                client.send(f"-1:El cliente {client.id} {client.name} se ha salido".encode())
            return "disconnected"
        else:
            # if we received a message, replace the <SEP> 
            # token with ": " for nice printing
            msg = msg.replace(self.separator_token, ": ")
        return msg


    def listen_to_pm(self, client_socket):
        while True:
            msg = self.listen(client_socket)
            id, msg = self.process_message(msg)
            print(id, id == "0", msg)
            if id == "-1":
                break
            elif id == "0":
                print(msg)
        client_socket.close()


    def accept_private_sockets(self):
      while True:
            # we keep listening for new connections all the time
            client_socket, _ = self.ss.accept()
            # # add the new connected client to connected sockets
            self.client_sockets.add(client_socket)
            # start a new thread that listens for each client's messages
            t = Thread(target=self.listen_to_pm, args=(client_socket,))
            # make the thread daemon so it ends whenever the main thread ends
            t.daemon = True
            # start the thread
            t.start()
