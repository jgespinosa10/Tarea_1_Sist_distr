# Chat

Aplicación que permite hacer un chat en formato LAN utilizando URL y puertos. Esta tiene una arquitectura basada en cliente-servidor para la comunicación comun entre muchos clientes y tiene una arquitectura P2P para la comunicación privada entre dos clientes. 

# Documentación 🎨
- [Chat](#chat)
  - [Instalación](#instalación)
    - [Dependencias](#dependencias)
    - [LAN](#lan)
  - [Ejecución](#ejecución)
    - [Servidor](#servidor)
    - [Cliente](#cliente)

## Instalación

### Dependencias
La aplicación corre en Python v.3.6.x y tiene las siguientes dependencias:

  Built-in:
  - `sockets`: Utilizada para la comunicación entre aplicaciones, se utiliza el protocolo TCP.  
  - `json`: Para comunicas objetos JSON entre clientes y servidor.  
  - `datetime`: Generar timestamps dentro de los mensaje.  
  - `threading`: Para poder paralelizar la ejecución tanto del servidor como del cliente.  
  - `signal`: Para poder manejar las interrupciones por teclado y evitar que se caiga la app.  
  - `sys`: Para obtener los parametros entregados en la linea de comando.  
  - `collection`: Sacamos la implementación de *stack* para tener todos los mensajes. la app.  
  - `os`: Para hacer llamadas al sistema operativo y terminar el proceso.  
  - `queue`: Para implementar la cola de mensajes.
  
  Instalable:
  - `pyngrok`: Para manejar la conexión mediante una URL pública.
  - `colorama`: Permite agregar colores a la linea de comando

Si es que no se tienen instaladas las dependencias `Instalable`, es necesario correr el siguiente comando en la terminal para instalar todas las dependencias requeridas

```bash
pip install -r requirements.txt
```

### LAN

Esta aplicación se puede correr en la LAN, para esto es necesario colocar un archivo `token.py`, en la ruta `server/lib/token.py`, el cual contiene la variable de entorno `NGROK_TOKEN` que nos entrega una URL y un puerto para así levantar la app en una LAN. Este token puede obtenerse en la página de [NGROK](https://ngrok.com/), especificamente [aquí](https://dashboard.ngrok.com/get-started/your-authtoken). Si es que no se desea obtener el token, se puede usar el siguiente token.

``` python
# server/lib/token.py
NGROK_TOKEN="1xmWa2wpyuTA5cYbGmzfSggcRa0_819kpwBEMgVP2d4B5sEDG"
```

Al tratar de conectarse siendo cliente se le pedirá que ingrese manualmente la dirección y el puerto del servidor al conectarse. Esto se puede evitar descomentando desde la linea 15 a la 19 en el archivo `client/main.py` (y comentando las lineas 26 a 33) y las lineas 28 a 30 en el archivo `server/main.py`. Esto creará un archivo `conection.txt` en la raiz del directorio que contendrá la URL y el puerto en que se levanta la app.

<br>

## Ejecución

Para ejecutar la aplicación es necesario ejecutar primero el servidor y luego los clientes que se necesiten

### Servidor

Estando en la raíz del repositorio ejecutamos lo siguiente en la terminal:

```bash
cd server
python3 ./main.py
```

Se puede utilizar el flag opcional `-n`, que indica cuantas personas deben ingresar al chat antes de que comience. Los chats se acumulan y sólo se pueden ver cuando han ingresado la cantidad de personas indicadas. Funciona de la siguiente manera:

```bash
cd server
python3 ./main.py -n N
```

donde N es la cantidad de clientes que se deben conectar para poder mostrar los mensajes.

**La primera vez corriendo el servidor, se va a descargar `ngrok`.**

<br>

### Cliente

Abrimos la terminal en la raiz del repositorio y ejectamos lo siguiente:

```bash
cd client
python3 ./main.py
```

Si es que no se automatizó el ingreso de la URL y el puerto se pedirán estas al iniciar el cliente
