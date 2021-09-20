# https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
from lib.client import Client
import os


if __name__ == "__main__":
    # URL and PORT are provided during server initialization

    while True:
        SERVER_HOST = input("Indicate server URL: ")
        SERVER_PORT = int(input("Indicate PORT: "))

        try:
            client = Client(SERVER_HOST, SERVER_PORT)
            break
        except Exception as e:
            print("Please check URL and PORT")

    try:
        client.run()
    except KeyboardInterrupt:
        print("Goodbye!")
        os._exit(0)
