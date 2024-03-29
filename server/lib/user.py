from threading import Lock


class User:
    def __init__(self, id, cs, name):
        # id del cliente
        self.id = id
        # socket y archivos de comunicacion asociado al cliente
        self.cs = cs
        # nombre del cliente
        self.name = name
        self.ip = None
        self.lock = Lock()

    # función que retorna la concatenación del id con el nombre del cliente
    def text(self) -> str:
        return f"{self.id}. {self.name}"

    def send(self, msg):
        with self.lock:
            self.write = self.cs.makefile('w')
            with self.write:
                self.write.write(msg + '\n')
                self.write.flush()

    def listen(self):
        self.read = self.cs.makefile('r')
        with self.read:
            msg = self.read.readline().strip()
        return msg

    def to_json(self):
        return {"id": self.id, "name": self.name, "ip": self.ip}
