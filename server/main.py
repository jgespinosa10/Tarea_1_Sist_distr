# Código recuperado de https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
from lib.helpers import process_args
from lib.server import Server

if __name__ == "__main__":
    n_clients, n_arg = process_args()
    # server's IP address
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5002 # port we want to use
    separator_token = "<SEP>" # we will use this to separate the client name & message
    server = Server(n_clients, n_arg, SERVER_HOST, SERVER_PORT, separator_token)
    server.run()