import socket

# prepara un socket para que este escuche al servidor.
def makeserversocket( self, backlog=5 ) -> socket.socket:
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    s.bind( ( '', 0 ) )
    s.listen( backlog )
    return s

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
def process_ip( str_ip ):
  ip = str_ip.split("-")
  ip[1] = int(ip[1])
  return tuple(ip)

# Función que no dependía del Objeto, por lo tanto puede ser un helper
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
def process_message(msg):
    msg = msg.split(":")
    id = msg[0]
    msg = ":".join(msg[1:])
    return id, msg