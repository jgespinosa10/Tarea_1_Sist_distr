
class User:
    def __init__(self, id, cs, name, read, write):
        # id del cliente
        self.id = id
        # socket y archivos de comunicacion asociado al cliente
        self.cs = cs
        self.read = read
        self.write = write
        # nombre del cliente
        self.name = name

    # función que retorna la concatenación del id con el nombre del cliente
    def text(self) -> str:
        return f"{self.id}. {self.name}"
    
    def send(self, msg):
      self.write = self.cs.makefile('w')
      with self.cs, self.write:
        self.write.write(msg + '\n')
        self.write.flush()
