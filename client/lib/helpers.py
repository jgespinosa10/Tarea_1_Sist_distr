import socket

# prepara un socket para que este escuche al servidor.
def makeserversocket( self, backlog=5 ) -> socket.socket:
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    s.bind( ( '', 0 ) )
    s.listen( backlog )
    return s

# Procesa los ips de los que clientes que se reciben
# por parte del servidor
def process_ip( str_ip ):
  ip = str_ip.split("-")
  ip[1] = int(ip[1])
  return tuple(ip)

# Toma un mensaje recibido del servidor y lo procesa para
# dividirlo en su id y el mensaje respectivo
def process_message(msg):
    msg = msg.split(":")
    id = msg[0]
    msg = ":".join(msg[1:])
    return id, msg