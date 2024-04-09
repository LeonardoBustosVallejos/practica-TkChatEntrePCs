import socket
import tkinter as tk
from threading import Thread
import tkinter.messagebox as messagebox
import time

HOST = 'localhost'  # Servidor al que se va a conectar
PORT = 8888  # Puerto del servidor al que se va a conectar

class ClientGUI:
    def __init__(self, master):
        self.master = master
        master.title('Cliente')

        self.name = tk.StringVar()
        self.name.set("Ganso")

        self.received_messages_text = tk.Text(master, height=10, width=50)
        self.received_messages_text.pack()

        self.message_entry = tk.Entry(master, width=50)
        self.message_entry.pack()

        self.name_entry = tk.Entry(master, width=50, textvariable=self.name)
        self.name_entry.pack()

        self.send_button = tk.Button(master, text='Enviar', command=self.send_message)
        self.send_button.pack()

        self.connected = False
        self.connect_to_server()

        # Al cerrar la ventana se detiene el cliente
        # y ejecuta la función on_close
        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.connected:# Si esta conectado enviar mensaje de desconexion
            self.socket.sendall('DISCONNECT'.encode())
        self.master.destroy()# Cerrar la ventana
        
    def update_client_dropdown(self):
        # Clear the current dropdown menu
        self.client_list.delete(0, tk.END)

        # Add each client to the dropdown menu
        for client in self.connections.keys():
            self.client_list.insert(tk.END, client)

    def connect_to_server(self):
        while True:
            try:
                # Crear un objeto de socket TCP
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Conectarse al servidor
                self.socket.connect((HOST, PORT))

                # Configurar la variable de conexión
                self.connected = True

                # Enviar el nombre al servidor
                self.socket.sendall(self.name.get().encode())

                # Iniciar el hilo de recepción de mensajes
                self.receive_thread = Thread(target=self.receive_messages)
                self.receive_thread.start()

                break  # Si se conectó, salir del bucle

            except Exception as e:
                print(e)

                # Configurar la variable de conexión
                self.connected = False

                # Esperar 5 segundos antes de intentar reconectar
                time.sleep(5)

    def receive_messages(self):
        while self.connected:
            try:
                # Recibir datos del servidor
                data = self.socket.recv(1024)

                # Si no hay datos, el servidor cerró la conexión
                if not data:
                    break

                # Agregar el mensaje recibido a la caja de texto
                self.received_messages_text.insert(tk.END, data.decode() + '\n')
                self.received_messages_text.see(tk.END)

            except Exception as e:
                print(e)
                self.connected = False
                self.socket.close()
                break

    def send_message(self):
        # Obtener el mensaje ingresado en el cuadro de texto
        message = self.message_entry.get()

        # Verificar si estamos conectados al servidor
        if not self.connected:
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: no hay conexión con el servidor.')
            return

        # Verificar si el socket aún está abierto
        if not self.socket._closed:
            # Enviar el mensaje al servidor
            self.socket.sendall(message.encode())

            # Borrar el cuadro de texto de mensaje
            self.message_entry.delete(0, tk.END)
        else:
            # Mostrar un mensaje de error si el socket está cerrado
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: la conexión con el servidor se ha perdido.')

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    client_gui = ClientGUI(root)
    root.mainloop()