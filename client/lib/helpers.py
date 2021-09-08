import socket

def makeserversocket( self, backlog=5 ) -> socket.socket:
    """ Constructs and prepares a server socket listening on the given 
    port.
    """
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
    s.bind( ( '', 0 ) )
    s.listen( backlog )
    return s