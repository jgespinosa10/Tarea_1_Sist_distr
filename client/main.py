# https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
from lib.client import Client


if __name__ == "__main__":
    # server's IP address
    # if the server is not on this machine, 
    # put the private (network) IP address (e.g 192.168.1.2)
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5002 # server's port
    separator_token = "<SEP>" # we will use this to separate the client name & message
    client = Client(SERVER_HOST, SERVER_PORT, separator_token)
    client.run()