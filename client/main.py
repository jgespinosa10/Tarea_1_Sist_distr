# https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
from lib.client import Client


if __name__ == "__main__":
    separator_token = "<SEP>" # we will use this to separate the client name & message

    # URL and PORT are provided during server initialization
    SERVER_HOST = input("Indicate server URL: ")
    SERVER_PORT = int(input("Indicate PORT: "))

    client = Client(SERVER_HOST, SERVER_PORT, separator_token)
    client.run()