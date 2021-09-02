## Documentación 🎨

Aplicación escrita en Python (v. 3.9.6)

Librerías utilizadas: <br>
  `sockets`: Utilizada para la comunicación entre aplicaciones, se utiliza el protocolo TCP<br>
  `colorama`: Para darle estilo a la consola<br>
  `random`: Generar elementos random dentro de la app<br>
  `threading`: Para poder paralelizar la ejecución tanto del servidor como del cliente<br>
  `signal`: Para poder manejar las interrupciones por teclado y evitar que se caiga la app<br>
  `sys`: Para obtener los parametros entregados en la linea de comando
  
La aplicación está basada en una arquitectura Cliente-Servidor, donde no se tiene una Base de Datos que almacene los datos a largo plazo. También para la comunicación privada entre dos personas se utiliza la arquitectura P2P, donde un cliente le pide al servidor que le comunique con el otro cliente para que este último abra un socket y así nuestro primer cliente pueda conectarse a este socket y así hablar directamente con el cliente saltandose así al servidor.


