import json
from queue import Queue
from threading import Thread, Lock
from time import sleep
from lib.helpers import ip_distance

class SubServer:
    def __init__(self, info, users, p2p, client):
        self.n_arg = info['n_arg']
        self.first_messages = info['first_messages']
        self.number_clients = info['number_clients']
        self.required_clients = info['required_clients']
        self.msg_queue = Queue()
        [self.msg_queue.put(i) for i in info['queue']]
        self.user_id = info['user_id']
        self.enough_clients = info['enough_clients']
        self.users = users
        self.p2p = p2p
        self.client = client
        self.clients_lock = Lock()

        self.queue_thread = Thread(target=self.send_messages)
        self.queue_thread.daemon = True

        self.select_server()

        if self.client.original_server_alive:
            self.inform_server({"id": "new_server", "client_id": self.client.id})

        self.queue_thread.start()

    def select_server(self):
        # Le decimos a todos los clientes que servidor deben elegir basandose en la distancia
        for id, user in self.users.items():
            # Esto es si es que el servidor inicial se cae se escoge si o si al client server
            if not self.client.original_server_alive:
                self.p2p.pm(id, "new_server-" + str(self.client.id))
            # Aqui se elige el servidor basandose en la distancia del cliente a ese servidor
            else:
                # Direcciones de los 3 puntos a revisar
                client_server_address = f"{self.client.client_hostname}-{self.client.port}"
                server_address = self.client.server_stats
                user_address = user["ip"] 
                # Calculamos distancias
                user_client_distance = ip_distance(client_server_address, user_address)
                user_server_distance = ip_distance(server_address, user_address)
                # revisamos que servidor tiene menor distancia al cliente
                # Servidor cliente
                if user_client_distance < user_server_distance:
                    print("redirigido al servidor cliente")
                    self.p2p.pm(id, "new_server-" + str(self.client.id))
                # Servidor inicial
                else:
                    print("redirigido al servidor inicial")
                    self.p2p.pm(id, "original_server-None")

    # Mensaje general a todos los clientes
    def broadcast(self, msg):
        for id, user in self.users.items():
            self.p2p.pm(id, msg)

    def inform_server(self, msg):
        # informa al servidor original que es el servidor actual
        msg = json.dumps(msg)
        self.client.write = self.client.cs.makefile('w')
        with self.client.write:
            self.client.write.write(msg + '\n')
            self.client.write.flush()

    def send_messages(self):
        while True:
            # if queue has msgs, remove first msg in queue and send it to all clients
            if not self.msg_queue.empty() and self.enough_clients:
                msg = self.msg_queue.get()
                with self.clients_lock:
                    self.broadcast(msg)
                if self.first_messages:
                    sleep(0.1)  # waiting for message to arrive
                if self.msg_queue.empty():
                    self.first_messages = False
