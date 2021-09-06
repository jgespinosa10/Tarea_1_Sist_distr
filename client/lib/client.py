import random
import socket
from colorama import init, Fore
from datetime import datetime
from threading import Thread

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

        # initialize TCP socket
        self.s = socket.socket()
        print(f"[*] Connecting to {self.SERVER_HOST}:{self.SERVER_PORT}...")
        # connect to the server
        self.s.connect((self.SERVER_HOST, self.SERVER_PORT))
        print("[+] Connected.")

        # prompt the client for a name
        self.name = input("Enter your name: ")
        print(f"{self.client_color}Hola {self.name}, bienvenid@ al chat!{Fore.RESET}")
        # make a thread that listens for messages to this client & print them
        t = Thread(target=self.listen_for_messages)
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        # start the thread
        t.start()
        
        self.s.send(f"\t{self.name} ha entrado a la sala".encode())

    # Función ejecutada en un thread, esta se encarga de escuchar la información del servidor
    def listen_for_messages(self):
        while True:
            try:
                message = self.s.recv(1024).decode()
                print(message, end="")
            # Se ejecuta cuando se sale del chat y cuando el servidor termina antes que el cliente
            except Exception:
                break

    def run(self):
        while True:
            # input message we want to send to the server
            to_send =  input()
            # a way to exit the program
            if to_send.lower() == 'q':
                break
            # add the datetime, name & the color of the sender
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
            to_send = f"{self.client_color}[{date_now}] {self.name}{self.separator_token}{to_send}{Fore.RESET}"
            # finally, send the message
            self.s.send(to_send.encode())

        # close the socket
        self.s.close()