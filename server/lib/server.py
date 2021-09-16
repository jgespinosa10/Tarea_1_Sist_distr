import socket
from queue import Queue
from threading import Thread, Lock
from lib.user import User
from lib.helpers import process_message
import json
from time import sleep


class Server:
    def __init__(self, n_clients, n_arg, SERVER_HOST, SERVER_PORT): 
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.n_arg = n_arg
        self.enough_clients = not n_arg
        self.first_messages = True
        self.number_clients = 0
        self.required_clients = n_clients
        self.msg_queue = Queue()
        self.clients_lock = Lock()
        self.user_id = 1

        self.clients = {}

        # create a TCP socket and make it reusable
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((SERVER_HOST, SERVER_PORT))

        self.queue_thread = Thread(target=self.send_messages)
        self.queue_thread.daemon = True


    def run(self):
        self.s.listen()
        print(f"[*] Listening as {self.SERVER_HOST}:{self.SERVER_PORT}")

        self.queue_thread.start()

        while True:
          client_socket, _ = self.s.accept()

          user = User(self.user_id, client_socket, None)
          t = Thread(target=self.listen_client, args=(user,))
          t.daemon = True
          t.start()

          self.user_id += 1

    def send_messages(self):
        while True:
            # if queue has msgs, remove first msg in queue and send it to all clients
            if not self.msg_queue.empty() and self.enough_clients:
                msg = self.msg_queue.get()
                print(msg)
                with self.clients_lock:
                  for id, user in self.clients.items():
                      user.send(msg)
                if self.first_messages:
                  sleep(0.1) # waiting for message to arrive
                if self.msg_queue.empty():
                  self.first_messages = False
    
    def listen_client(self, user):
        msg = user.listen()
        msg = msg.split("-")
        user.ip = "-".join(msg[:2])

        print(f"[+] {user.ip} connected.")

        user.name = "-".join(msg[2:])

        clients = {}
        clients['self'] = user.id
        for id, client in self.clients.items():
            clients[id] = client.to_json()

        user.send(json.dumps(clients))
        user.listen()

        with self.clients_lock:
          self.clients[int(user.id)] = user
        # update the minimum of clients condition
        self.number_clients += 1
        if self.n_arg and self.number_clients >= self.required_clients:
            self.enough_clients = True
        # with self.queue_lock: 
        self.msg_queue.put(f"1-{user.id};{user.ip};{user.name}")
        
        while True:
            msg = user.listen()
            if msg == "":
              id, msg = "k", ""
            else:
              id, msg = process_message(msg)
            if id == "0":
                  print("en colando")
                  self.msg_queue.put("0-" + msg)
            elif id == "k":
                with self.clients_lock:
                  del self.clients[int(user.id)]
                  self.msg_queue.put(f"k-{user.id}-{user.name} ha salido del chat")
                  break
                



