# Documentación 🎨

Aplicación escrita en Python (v. 3.9.6)

Librerías utilizadas:

  `sockets`: Utilizada para la comunicación entre aplicaciones, se utiliza el protocolo TCP.  
  `colorama`: Para darle estilo a la consola.  
  `random`: Generar elementos random dentro de la app.  
  `threading`: Para poder paralelizar la ejecución tanto del servidor como del cliente.  
  `signal`: Para poder manejar las interrupciones por teclado y evitar que se caiga la app.  
  `sys`: Para obtener los parametros entregados en la linea de comando.

Para instalar las librerías, puedes correr el comando en esta carpeta:

```bash
pip install -r requirements.txt
```
  
La aplicación está basada en una arquitectura Cliente-Servidor, donde no se tiene una Base de Datos que almacene los datos a largo plazo. También para la comunicación privada entre dos personas se utiliza la arquitectura P2P, donde un cliente le pide al servidor que le comunique con el otro cliente para que este último abra un socket y así nuestro primer cliente pueda conectarse a este socket y así hablar directamente con el cliente saltandose así al servidor.

Para ejecutar la aplicación es necesario ejecutar primero el servidor, para esto nos colocamos en el directorio del servidor y ejecutamos el código de este:

```bash
cd server
python3 ./main.py
```

Se puede utilizar el flag opcional `-n`, que indica cuantas personas deben ingresar al chat antes de que comience. Los chats se acumulan y sólo se pueden ver cuando han ingresado la cantidad de personas indicadas. Funciona de la siguiente manera:

```bash
python3 ./main.py -n N
```

donde N es la cantidad de clientes que se deben conectar para poder mostrar los mensajes.

Luego, abrimos la terminal en el directorio del cliente y ejectamos el código de este:

```bash
cd client
python3 ./main.py
```
