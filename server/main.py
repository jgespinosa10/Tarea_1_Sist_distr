# Código recuperado de https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
from lib.helpers import process_args
from lib.server import Server
from lib.token import NGROK_TOKEN
from pyngrok import ngrok

if __name__ == "__main__":
    # recibimos los posibles argumentos utilizados al iniciar el servidor 
    n_clients, n_arg = process_args()
    # server's IP address
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5002 # port we want to use
    server = Server(n_clients, n_arg, SERVER_HOST, SERVER_PORT)

    ### Set up an ngrok tunnel to connect a public URL to localhost
    # Seteamos al token de ngrok utilizaremos
    ngrok.set_auth_token(NGROK_TOKEN)
    # Creamos el ssh tunnel para poder recibir una URL y puerto a utilizar, estos quedan en las variables descritas a continuación
    ssh_tunnel = ngrok.connect(SERVER_PORT, "tcp")
    print("URL:", ssh_tunnel.public_url.split('/')[-1].split(':')[0])
    print("PORT:", ssh_tunnel.public_url.split(':')[-1])

    try:
      server.run()
    except KeyboardInterrupt:
      print("Shutting down server...")
    ngrok.kill()