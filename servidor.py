import json
import socket  
import threading
import sqlite3


host = '127.0.0.1' # localhost
port = 55555 


# Crear Socket para la red
#Se almacena el socket en la variable server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP

#Se pasan los datos de conexion al socket
server.bind((host, port)) # Se enlazaa el servidor con el host y el puerto
server.listen()
print(f"Servidor Ejecutandose en {host}:{port}")


clientes = [] # Alamcena las conexiones de los usuarios
nombreUsuarios = [] # Almacena los nombres de usuarios de los clientes

# ------------------ Manejo de conexiones y Mensajes ------------------

#Enviar el mensaje a todos los clientes
def broadcast(message, _client):
    for client in clientes: # Para cada cliente en la lista de clientes
        if client == _client: # No enviar el mensaje al cliente que lo envio
            if( message == 'Obtener Json'.encode('utf-8')):	# Si el mensaje es igual a Obtener Json - Codifico el mensaje 
                generarJson() # Genero el archivo .json
                with open('./results/'+'usuarios'+'.json', 'r') as j: # Abro el archivo .json
                    mydata = json.load(j) # Cargo el archivo .json
                    client.send(str(mydata).encode('utf-8')) # Envio el archivo .json al cliente

            # client.send()
                # client.send(respuesta)


#Funcion para manejar mensajes de cada usuario
def manejar_mensajes(cliente):
    while True:
        try: #
            # Se optiene el mensaje del cliente
            message = cliente.recv(1024) # Se recibe el mensaje del cliente
            broadcast(message, cliente) # Se envia el mensaje a todos los clientes
        except:
            index = clientes.index(cliente) # Se obtiene el indice del cliente
            nombreUsuario = nombreUsuarios[index] # Se obtiene el nombre de usuario del cliente
            broadcast(f"ChatBot: {nombreUsuario} Desconectado".encode('utf-8'), cliente) # Se envia el mensaje de que el cliente se desconecto
            clientes.remove(cliente) # Se elimina el cliente de la lista de clientes
            nombreUsuarios.remove(nombreUsuario) # Se elimina el nombre de usuario de la lista de nombres de usuario
            cliente.close() # Se cierra la conexion del cliente
            break


#Funcion para manejar la conexion de los clientes
def recibir_conexiones(): # Se ejecuta en un hilo
    while True: 
        cliente, address = server.accept() # Se acepta la conexion del cliente

        cliente.send("@nombreUsuario".encode("utf-8")) # Se envia el mensaje para que el cliente envie su nombre de usuario
        nombreUsuario = cliente.recv(1024).decode('utf-8') # Se recibe el nombre de usuario del cliente

        clientes.append(cliente) # Se agrega el cliente a la lista de clientes
        nombreUsuarios.append(nombreUsuario) # Se agrega el nombre de usuario a la lista de nombres de usuario

        print(f"{nombreUsuario} esta conectado con {str(address)}") # Se imprime el nombre de usuario y la direccion del cliente

        message = f"ChatBot: {nombreUsuario} entró al chat!".encode("utf-8") # Se crea el mensaje de que el cliente se conecto
        broadcast(message, cliente) # Se envia el mensaje a todos los clientes
        cliente.send("Conectado al servidor - Para poder optener el .json mande el mensaje Obtener Json".encode("utf-8")) # Se envia el mensaje de que el cliente se conecto al servidor

        thread = threading.Thread(target=manejar_mensajes, args=(cliente,)) # Se crea un hilo para manejar los mensajes del cliente
        thread.start() # Se inicia el hilo

# ------------------Optener Json de la base de datos------------------

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# conectarse a bases de datos SQlite
def openConnection(pathToSqliteDb):
    connection = sqlite3.connect(pathToSqliteDb)
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    return connection, cursor

# Obtener todos los registros de la tabla
def getAllRecordsInTable(table_name, pathToSqliteDb):
    conn, curs = openConnection(pathToSqliteDb)
    conn.row_factory = dict_factory
    curs.execute("SELECT * FROM '{}' ".format(table_name))
    # devuelvo un array
    results = curs.fetchall()
    # Cerrar conexion
    conn.close()
    return json.dumps(results)

# convertir sqlite a json
def sqliteToJson(pathToSqliteDb):
    connection, cursor = openConnection(pathToSqliteDb)
    # seleccionar todas las tablas de la base de datos
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    # para cada una de las tablas , seleccionar todos los registros de la tabla
    for table_name in tables:
        # Obtener los registros de la tabla
        results = getAllRecordsInTable(table_name['name'], pathToSqliteDb)

        # generar y guardar archivos JSON con el nombre de la tabla para cada una de las tablas de la base de datos y guardar en la carpeta de resultados
        with open('./results/'+table_name['name']+'.json', 'w') as the_file:
            the_file.write(results)
    # Cerrar conexion
    connection.close()
    
# Generar Archivo .json
def generarJson():
    if __name__ == '__main__':
        # ruta de la base de datos
        pathToSqliteDb = 'ejemplo.db'
        sqliteToJson(pathToSqliteDb)

# ------------------Fin Optener Json de la base de datos------------------

recibir_conexiones() # Se ejecuta la funcion para manejar las conexiones de los clientes

