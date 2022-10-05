import socket   
import threading

nombreUsuario = input("Ingrese su nombre de usuario: ")

host = '127.0.0.1' # localhost
port = 55555 

# Crear Socket para la red
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
cliente.connect((host, port)) # Se conecta al servidor


#Funcion para manejar los mensajes del servidor
def recibirMensaje():
    while True:
        try:
            mensaje = cliente.recv(1024).decode('utf-8') # Se recibe el mensaje del servidor

            if mensaje == "@nombreUsuario": 
                cliente.send(nombreUsuario.encode("utf-8")) # Se envia el nombre de usuario al servidor
            else:
                print(mensaje)  # Se imprime el mensaje
        except:
            print("Chat Finalizado - Te has desconectado") # Se imprime el mensaje de que el cliente se desconecto
            cliente.close # Se cierra la conexion
            break

def escribirMensaje():
    while True:
        mensaje = input() # Se escribe el mensaje
        if(mensaje == "exit"): # Si el mensaje es exit, se cierra la conexion
            cliente.close()
            break
        else: # Si no, se envia el mensaje al servidor
            # mensaje = f"{mensaje}" # Se agrega el nombre de usuario al mensaje
            cliente.send(mensaje.encode('utf-8')) # Se envia el mensaje al servidor

receive_thread = threading.Thread(target=recibirMensaje) # Se crea el hilo para recibir mensajes
receive_thread.start() # Se inicia el hilo

write_thread = threading.Thread(target=escribirMensaje) # Se crea el hilo para escribir mensajes
write_thread.start() # Se inicia el hilo