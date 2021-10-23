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

# Calcula la distancia entre 2 IPs, donde primero se revisa la IP y si es 0, entonces se revisa el puerto
def ip_distance(ipPort1: str, ipPort2: str) -> int:

    ip1, port1 = ipPort1.split("-")
    ip2, port2 = ipPort2.split("-")

    ip_1 = [int(i) for i in ip1.split(".")]
    ip_2 = [int(i) for i in ip2.split(".")]
    
    distance = 0
    [distance + (ip_1[i] - ip_2[i])*10**i for i in range(3)]
    distance = abs(distance)

    if distance == 0:
        distance = abs(int(port1) - int(port2))

    return distance
    