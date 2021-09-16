import sys

# Función que recibe los argumentos de la linea de comando
def process_args():
    n_clients = 1
    n_arg = False
    for i, args in enumerate(sys.argv):
        if (args == "-n"):
            n_clients = int(sys.argv[i+1])
            n_arg = True
    return n_clients, n_arg


def process_message(msg):
    msg = msg.split("-")
    id = msg[0]
    msg = ":".join(msg[1:])
    return id, msg