import socket
from collections import deque
from colorama import Fore, init
from threading import Thread
import json
from lib.user import User


class Server:
    def __init__(self, n_clients, n_arg, SERVER_HOST, SERVER_PORT, separator_token):
        # init variables
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.separator_token = separator_token
        # n_arg = true if -n present in args
        self.n_arg = n_arg
        self.enough_clients = not n_arg
        self.number_clients = 0
        self.required_clients = n_clients
        self.msg_queue = deque()
        self.user_id = 1
        
        # init colors
        init()
        # initialize list/set of all connected client's sockets
        self.client_sockets = set()
        # create a TCP socket
        self.s = socket.socket()
        # make the port as reusable port
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to the address we specified
        self.s.bind((SERVER_HOST, SERVER_PORT))
        # Aquí se inserta el "n" que define la cantidad de personas a conectar
        self.s.listen()
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

        # Add thread to check message queue and send messages to all clients
        queue_thread = Thread(target=self.send_messages)
        queue_thread.daemon = True
        queue_thread.start()


    def run(self):
        while True:
            # we keep listening for new connections all the time
            client_socket, _ = self.s.accept()
            # clients connected + 1
            self.number_clients += 1
            if self.n_arg and self.number_clients >= self.required_clients:
                self.enough_clients = True
            # create user object
            user = User(self.user_id, client_socket, None)
            # add the new connected client to connected sockets
            self.client_sockets.add(user)
            # start a new thread that listens for each client's messages
            t = Thread(target=self.listen_for_client, args=(user,))
            # make the thread daemon so it ends whenever the main thread ends
            t.daemon = True
            # start the thread
            t.start()
            # Count id's
            self.user_id += 1

    def listen(self, user):
        try:
            # keep listening for a message from `cs` socket
            msg = user.cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"{Fore.RED}[!] Error: {e}{Fore.RESET}")
            self.client_sockets.remove(user)
            user.cs.close()
            for client in self.client_sockets:
                client.cs.send(f"0-El cliente {client.id} {client.name} se ha salido".encode())
            return "disconnected"
        else:
            # if we received a message, replace the <SEP> 
            # token with ": " for nice printing
            msg = msg.replace(self.separator_token, ": ")
        return msg

    def process_message(self, msg):
        msg = msg.split("-")
        mid = msg[0]
        msg = ":".join(msg[1:])
        return mid, msg

    # Función ejecutada en un thread, esta se encarga de escuchar la información enviada desde el cliente 
    def listen_for_client(self, user: User):
        """
        This function keep listening for a message from `cs` socket
        Whenever a message is received, broadcast it to all other connected clients
        """
        msg = self.listen(user)
        if msg == "-1":
            return
        user.ip = msg
        print(f"[+] {user.ip} connected.")

        msg = self.listen(user)
        user.name = msg
        self.send_users(user)
        while True:
            msg = self.listen(user)
            id, msg = self.process_message(msg)
            if id == "-1":
                break
            elif id == "0":
                self.msg_queue.append(msg)
            elif id == "2":
                pass

    def send_users(self, user):
        users_name = dict()
        users_ip = dict()

        for client in self.client_sockets:
            # Se envia a cada cliente el nombre y la ip del nuevo cliente
            if client != user:
                try:
                    client.cs.send(f"1-{user.id};{user.ip};{user.name}".encode())
                except ConnectionAbortedError:
                    break

                # Guarda la direccion y nombre de los clientes antiguos para enviarlos al nuevo cliente
                users_name[client.id] = client.name

                users_ip[client.id] = client.ip

        # Se envia la información de los clientes al nuevo cliente
        users = {"name": users_name, "ip": users_ip}
        user.cs.send(json.dumps(users).encode())


    def send_messages(self):
        while True:
            # if queue has msgs, remove first msg in queue and send it to all clients
            if len(self.msg_queue) != 0 and self.enough_clients:
                msg = self.msg_queue.popleft()
                msg += '\n'
                print(msg, end="")
                for user in self.client_sockets:
                    try: 
                        user.cs.send(("0-" + msg).encode())
                    except ConnectionAbortedError:
                        break
