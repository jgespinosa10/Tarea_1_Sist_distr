# Client-Server from # https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
# Peer to peer from http://cs.berry.edu/~nhamid/p2p/framework-python.html

import random
import socket
import traceback
from colorama import init, Fore
from datetime import datetime
from threading import Thread

from lib.BTPeerConnection import BTPeerConnection

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
        self.cs = socket.socket()
        print(f"[*] Connecting to {self.SERVER_HOST}:{self.SERVER_PORT}...")
        # connect to the server
        self.cs.connect((self.SERVER_HOST, self.SERVER_PORT))
        print("[+] Connected.")

        # prompt the client for a name
        self.name = input("Enter your name: ")
        print(f"{self.client_color}Hola {self.name}, bienvenid@ al chat!{Fore.RESET}")
        self.cs.send(self.name.encode())
        #recieve list of id's
        try:
            message = self.cs.recv(1024).decode()
            self.users = [msg.split(",") for msg in message[1:].split(";")]
            if not self.users[0][0]:
                self.users = dict()
            else:
                self.users = {msg[0]: msg[1] for msg in self.users}
        except Exception:
            # Se ejecuta cuando se sale del chat y cuando el servidor termina antes que el cliente
            return
        # make a thread that listens for messages to this client & print them
        t = Thread(target=self.listen_for_messages)
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        # start the thread
        t.start()

        ### Peer 2 Peer connection
        

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
                    self.users[user[0]] = user[1]
            # Se ejecuta cuando se sale del chat y cuando el servidor termina antes que el cliente
            except Exception:
                break

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
            msg = msg.split(":")
            id = msg[0]
            msg = ":".join(msg[1:])
            # a way to exit the program
            if id == '-1':
                break
            elif id == '0':
                # add the datetime, name & the color of the sender
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                to_send = f"{self.client_color}[{date_now}] {self.name}{self.separator_token}{msg}{Fore.RESET}"
                # finally, send the message
                self.cs.send(to_send.encode())
            elif id.isnumeric() and id in self.users:
                # stablish p2p connection and send message
                pass
            else:
                print("Elige un id válido")

        # close the socket
        self.cs.close()

    def print_users(self):
        text= ""
        for user in self.users.items():
            text += f" {user[0]}. - {user[1]}\n"
        return text
    
    ## Funtions for peer 2 peer
    # Creates a socket for the client to listen to another clients
    def makeserversocket( self, backlog=5 ):
        """ Constructs and prepares a server socket listening on the given 
        port.
        """
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        s.bind( ( '', 0 ) )
        s.listen( backlog )
        return s

    
    def __handlepeer( self, clientsock ):

        host, port = clientsock.getpeername()
        peerconn = BTPeerConnection( None, host, port, clientsock, debug=False )
        
        try:
            msgtype, msgdata = peerconn.recvdata()
            if msgtype: msgtype = msgtype.upper()
            if msgtype in self.handlers:
                self.handlers[ msgtype ]( peerconn, msgdata )
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
        
        peerconn.close()

        # end handlepeer method

    
    def peer2peer_loop( self ):
        s = self.makeserversocket()
        s.settimeout(2)

        while not self.shutdown:
            try:
                clientsock, clientaddr = s.accept()
                clientsock.settimeout(None)

                t = Thread( target = self.__handlepeer, args = [ clientsock ] )
                t.start()
            except KeyboardInterrupt:
                self.shutdown = True
                continue
            except:
                traceback.print_exc()
                continue
        s.close()

        def sendtopeer( self, peerid, msgtype, msgdata, waitreply=True ):
	        if self.router:
	            nextpid, host, port = self.router( peerid )
	        if not self.router or not nextpid:
	            return None
	        return self.connectandsend( host, port, msgtype, msgdata, pid=nextpid, waitreply=waitreply )

        
    def connectandsend( self, host, port, msgtype, msgdata, pid=None, waitreply=True ):
        msgreply = []   # list of replies
        try:
            peerconn = BTPeerConnection( pid, host, port)
            peerconn.senddata( msgtype, msgdata )
            
            if waitreply:
                onereply = peerconn.recvdata()
                while (onereply != (None,None)):
                    msgreply.append( onereply )
                    onereply = peerconn.recvdata()
            peerconn.close()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
        
        return msgreply
