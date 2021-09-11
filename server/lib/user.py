
class User:
    def __init__(self, id, cs, name):
        # id del cliente
        self.id = id
        # socket asociado al cliente
        self.cs = cs
        # nombre del cliente
        self.name = name

    # función que retorna la concatenación del id con el nombre del cliente
    def text(self) -> str:
        return f"{self.id}. {self.name}"