
class User:
    def __init__(self, id, cs, name):
        self.id = id
        self.cs = cs
        self.name = name

    def text(self):
        return f"{self.id}. {self.name}"