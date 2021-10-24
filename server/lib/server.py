import socket
from queue import Queue
from threading import Thread, Lock
from lib.user import User
from lib.helpers import ip_distance
import random
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
        self.server_id = None

        self.clients = {}

        # create a TCP socket and make it reusable
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((SERVER_HOST, SERVER_PORT))

        self.queue_thread = Thread(target=self.send_messages)
        self.queue_thread.daemon = True

        self.timer = Thread(target=self.add_server)
        self.timer.daemon = True

    def run(self):
        '''
        Función que corre al comenzar el thread, está encargada de 
        recibir a todos los clientes que deseen conectarse
        '''
        self.s.listen()
        print(f"[*] Listening as {self.SERVER_HOST}:{self.SERVER_PORT}")

        self.queue_thread.start()
        self.timer.start()

        while True:
            client_socket, _ = self.s.accept()

            self.add_new_user(id=str(self.user_id), cs=client_socket)            
            self.user_id += 1

    def send_messages(self):
        '''
        Función encargada de enviar cualquier tipo de mensaje
        '''
        while True:
            # if queue has msgs, remove first msg in queue and send it to all clients
            if not self.msg_queue.empty() and self.enough_clients:
                msg = self.msg_queue.get()
                with self.clients_lock:
                    for id, user in self.clients.items():
                        user.send(msg)
                if self.first_messages:
                    sleep(0.1)  # waiting for message to arrive
                if self.msg_queue.empty():
                    self.first_messages = False

    def listen_client(self, user):
        '''
        Función que escucha lo que hace un cliente en especifico,
        esta se monta sobre un thread distinto
        '''
        # Esto es en el caso en que el cliente se conecte por primera vez al chat
        # en caso contrario ya tenemos su ip y nombre
        if not user.ip and not user.name:
            msg = user.listen()
            user.ip = msg["hostname"]
            user.name = msg["name"]

        print(f"[+] {user.ip} connected.")

        clients = {}
        clients['self'] = user.id
        for id, client in self.clients.items():
            clients[id] = client.to_json()
        
        user.send(json.dumps(clients))
        user.listen()

        user.send({"id": "init", "hostname": self.SERVER_HOST, "port": self.SERVER_PORT})
        user.listen()

        with self.clients_lock:
            self.clients[user.id] = user
        # update the minimum of clients condition
        self.number_clients += 1
        if self.n_arg and self.number_clients >= self.required_clients:
            self.enough_clients = True
        # with self.queue_lock:
        self.msg_queue.put({"id": "1", "user_id": user.id, "user_ip": user.ip, "user_name": user.name})

        if not self.server_id is None:
            # Direcciones de los 3 puntos a revisar
            client_server_address = self.clients[self.server_id].ip
            server_address = f"{self.SERVER_HOST}-{self.SERVER_PORT}"
            user_address = user.ip
            # Calculamos distancias
            user_client_distance = ip_distance(client_server_address, user_address)
            user_server_distance = ip_distance(server_address, user_address)
            # revisamos que servidor tiene menor distancia al cliente
            # Servidor cliente
            if user_client_distance < user_server_distance:
                print(f"{user.name} redirigido al servidor cliente")
                user.send({"id": "new_server", "client_id": str(self.server_id)})
            else:
                print(f"{user.name} se queda en el servidor actual")

        try: 
            while True:
                # Escuchamos el mensaje del usuario
                msg = user.listen()
                # Si el mensaje es vacio, entonces un usuario se ha salido
                if msg == "":
                    id, msg = "k", ""
                else:
                    id = msg["id"]

                # Revisamos que se hace con el mensaje entregado
                # 0 significa mensaje correcto
                if id == "0":
                    # Agregar mensaje a la cola general entre 2 servidores
                    print("en colando mensaje")
                    self.msg_queue.put({"id": "0", "msg": msg["msg"]})
                # k significa que se ha salido una persona
                elif id == "k":
                    with self.clients_lock:
                        del self.clients[user.id]
                        self.msg_queue.put({"id": "k", "user_id": user.id, "user_name": user.name})
                        self.number_clients -= 1
                        break
                # new_server significa que un nuevo cliente es servidor
                elif id == "new_server":
                    self.server_id = msg["client_id"]
                    print(f"Se eligió a {self.clients[self.server_id].name} como nuevo servidor")
                    self.select_server()

        except ConnectionResetError:
            pass

    def add_server(self):
        '''
        Funcion que luego de 30 segundos añade a otro servidor, este
        es montado en algun cliente
        '''
        while True:
            sleep(5)

            if self.number_clients > 0:
                user = random.choice(list(self.clients.values()))

                info = {}
                info['first_messages'] = self.first_messages
                info['number_clients'] = self.number_clients
                info['n_arg'] = self.n_arg
                info['required_clients'] = self.required_clients
                info['queue'] = list(self.msg_queue.queue)
                info['user_id'] = self.user_id
                info['enough_clients'] = self.enough_clients

                user.send({"id": "server", "info": json.dumps(info)})
                print(f"Se añade al cliente {user.id} como segundo servidor")
                break

    def select_server(self):
        '''
        Función que selecciona a que servidores deben ir los clientes
        luego de hacer un cambio en los servidores actuales
        '''

        '''!!!!!!!!!!!!!!!!!!!!! Falta eliminar los clientes que ya no están en el servidor inicial y se cambian de servidor !!!!!!!!!!!!!!!!!!!!'''


        # Le decimos a todos los clientes que servidor deben elegir basandose en la distancia
        for id, user in self.clients.items():
            if id == self.server_id:
                continue
            # Direcciones de los 3 puntos a revisar
            client_server_address = self.clients[self.server_id].ip
            server_address = f"{self.SERVER_HOST}-{self.SERVER_PORT}"
            user_address = user.ip
            # Calculamos distancias
            user_client_distance = ip_distance(client_server_address, user_address)
            user_server_distance = ip_distance(server_address, user_address)
            # revisamos que servidor tiene menor distancia al cliente
            # Servidor cliente
            if user_client_distance < user_server_distance:
                print(f"{user.name} redirigido al servidor cliente")
                user.send({"id": "new_server", "client_id": str(self.server_id)})
                # Eliminamos a este cliente de la lista

    def add_new_user(self, id=None, cs=None, name=None, ip=None):
        '''
        Función que agrega un nuevo cliente a este servidor,
        hacerlo así nos permite agregar un cliente que ya está conectado y 
        tambien a uno que no se ha conectado todavia.
        '''
        user = User(id, cs, name, ip)
        t = Thread(target=self.listen_client, args=(user,))
        t.daemon = True
        t.start()