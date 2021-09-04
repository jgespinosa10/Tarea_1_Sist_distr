import socket
from threading import Thread
from colorama import Fore, init
from collections import deque

class Server:
    def __init__(self, n_clients,SERVER_HOST, SERVER_PORT, separator_token):
        # init variables
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.separator_token = separator_token
        self.msg_queue = deque()
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
        self.s.listen(n_clients)
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
        # Add thread to check message queue and send messages to all clients
        queue_thread = Thread(target=self.send_messages)
        queue_thread.daemon = True
        queue_thread.start()

    def run(self):
        while True:
            # we keep listening for new connections all the time
            client_socket, client_address = self.s.accept()
            print(f"[+] {client_address} connected.")
            # add the new connected client to connected sockets
            self.client_sockets.add(client_socket)
            # start a new thread that listens for each client's messages
            t = Thread(target=self.listen_for_client, args=(client_socket,))
            # make the thread daemon so it ends whenever the main thread ends
            t.daemon = True
            # start the thread
            t.start()

    # Función ejecutada en un thread, esta se encarga de escuchar la información enviada desde el cliente 
    def listen_for_client(self, cs):
        """
        This function keep listening for a message from `cs` socket
        Whenever a message is received, broadcast it to all other connected clients
        """
        while True:
            try:
                # keep listening for a message from `cs` socket
                msg = cs.recv(1024).decode()
            except Exception as e:
                # client no longer connected
                # remove it from the set
                print(f"{Fore.RED}[!] Error: {e}{Fore.RESET}")
                self.client_sockets.remove(cs)
                cs.close()
                for client_socket in self.client_sockets:
                    client_socket.send(f"El cliente se ha salido".encode())
                break
            else:
                # if we received a message, replace the <SEP> 
                # token with ": " for nice printing
                msg = msg.replace(self.separator_token, ": ")

            self.msg_queue.append(msg)


    def send_messages(self):
        while True:
            # if queue has msgs, remove first msg in queue and send it to all clients
            if len(self.msg_queue) != 0:
                msg = self.msg_queue.popleft()
                print(msg)
                for client_socket in self.client_sockets:
                    client_socket.send(msg.encode())