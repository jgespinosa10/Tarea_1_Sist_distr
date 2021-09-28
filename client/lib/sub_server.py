from queue import Queue
from threading import Thread, Lock
from time import sleep


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

        self.broadcast("new_server-" + str(self.client.id))
        self.inform_server("new_server-" + str(self.client.id))

        self.queue_thread.start()

    def broadcast(self, msg):
        for id, user in self.users.items():
            self.p2p.pm(id, msg)

    def inform_server(self, msg):
        # informa al servidor original que es el servidor actual
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
