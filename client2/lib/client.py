# Client-Server from # https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
# Peer to peer from http://cs.berry.edu/~nhamid/p2p/framework-python.html

import socket
from datetime import datetime
from threading import Thread
from lib.helpers import process_input, prepare_message, process_message, print_users
from lib.p2p import P2P
import json

class Client:
    def __init__(self, SERVER_HOST, SERVER_PORT):
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.server_alive = True
        self.users = dict()
        self.id = None

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
              msg =  input("".join([
                  "Menú:\n",
                  "-1. Salir del chat\n",
                  " 0. Enviar a todos\n",
                  print_users(self),
                  "Escribe de la siguiente forma: {id}: {mensaje}\n\n"
                ]))
              if not self.server_alive:
                break

              id, msg = process_input(msg)

              if id == "-1":
                  raise KeyboardInterrupt
              elif id == "0":
                  self.send(prepare_message(self, msg))
              elif id in self.users:             
                  self.p2p.pm(id, prepare_message(self, msg, private=True))

              else:
                  print("Elige un id válido")
          except KeyboardInterrupt:
              print("cerrando...")
              self.send("k-dead")

              self.p2p.die()

              raise KeyboardInterrupt

    
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
            if self.id != int(user[0]):
              self.users[user[0]] = {'id': user[0], 'name': user[2], 'ip': user[1]}
            print(f"¡{user[0]}: {user[2]} ha entrado a la sala!\n")
        elif id == "k":
            msg = msg.split('-')
            id = msg[0]
            msg = "-".join(msg[1:])
            del self.users[id]
            print(msg)
            
 