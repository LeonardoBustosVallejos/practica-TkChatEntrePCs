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
        master.geometry('800x380')
        # Al cerrar la ventana se detiene el cliente
        # y ejecuta la función on_close
        master.protocol("WM_DELETE_WINDOW", self.on_close)

# ======================================= IZQUIERDA DE LA GUI =======================================
        self.name = tk.StringVar()
        self.name.set("Pato")

        # Text para mostrar los mensajes
        self.log_text = tk.Text(master, height=10, width=50, state=tk.DISABLED)# Por default el text es de solo lectura
        self.log_text.place(x=20, y=50)

        # Text para escribir los mensajes
        self.message_text = tk.Text(master, height=3,width=50)
        self.message_text.place(x=20, y=270)

        # Label para el nombre del usuario
        self.name_label = tk.Label(master, text='USUARIO: ')
        self.name_label.place(x=170, y=15)
        self.name_entry = tk.Label(master, textvariable=self.name)
        self.name_entry.place(x=230, y = 15)

        # Conectar al server
        self.Connect_button = tk.Button(master, text='Conectar', state=tk.DISABLED)
        self.Connect_button.place(x=130, y=230)

        # Desconectar del server
        self.connect_button = tk.Button(master, text='Desconectar')
        self.connect_button.place(x=230, y=230)

        self.send_button = tk.Button(master, text='Enviar', command=self.send_message)
        self.send_button.place(x=180, y=330)
# =================================================================================================

# ======================================= DERECHA DE LA GUI =======================================

        # Boton "Global"
        self.global_button = tk.Button(master, text='Global', state=tk.DISABLED, command=lambda: self.select_client('Global'))
        self.global_button.place(x=610, y=15)

        # Canvas y scrollbar para los botones de los clientes
        self.canvas = tk.Canvas(master, width=265, height=200, bg='white')
        self.scrollbar = tk.Scrollbar(master, command=self.canvas.yview)

        # Configurar el canvas para que se pueda desplazar con la scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # crea un frame para los botones
        self.buttons_frame = tk.Frame(self.canvas, bg='white', padx=3, pady=3)
        self.buttons_per_row = 5

        # añade los botones al frame y los coloca en el canvas
        self.canvas.create_window((0, 0), window=self.buttons_frame, anchor='nw')

        # Coloca el canvas y la scrollbar en la ventana
        self.canvas.place(x=500, y=50)
        self.scrollbar.place(x=770, y=50, height=200)
        self.current_row = 0
        self.current_row_width = 0
        self.canvas_width = 260 - 10

        # Configurar el evento de desplazamiento del canvas para que se ajuste al tamaño del frame
        self.buttons_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        # Boton "Eliminar desconectados"
        self.remove_offline_button = tk.Button(master, text='Eliminar\ndesconectados')
        self.remove_offline_button.place(x=510, y=280)

        # Destinatarios
        self.messages_to_label = tk.Label(master, text='Mensaje a:')
        self.messages_to_label.place(x=620, y=260)
        # Text para mostrar los destinatarios
        self.messages_to_text = tk.Text(master, bg='#f0f0f0', height = 4, width=18, state=tk.DISABLED)
        self.messages_to_text.place(x=620, y=280)
# =================================================================================================

# ======================================= VARIABLES DE LA GUI =======================================
        # Variable para saber si esta conectado
        self.connected = False
        # Botones de los clientes
        self.client_buttons = {}
        # Guardar las conexiones
        self.connections = {}
        # clientes seleccionados para enviar mensajes
        self.selected_clients = []
        # Conectar al servidor
        self.connect_to_server()
# =================================================================================================

# ===================================== FUNCIONES UTILITARIAS =====================================
    # Habilitar la caja de texto de log
    def enable_log(self):
        self.log_text.config(state='normal')
    # Deshabilitar la caja de texto de log
    def disable_log(self):
        self.log_text.config(state='disabled')
    # Agregar un mensaje a la caja de texto de log
    def log(self, message):
        self.enable_log()
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.disable_log()
# =================================================================================================

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

                self.log('Conectado al servidor')
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
                self.enable_log()
                self.log_text.insert(tk.END, data.decode() + '\n')
                self.log_text.see(tk.END)
                self.disable_log()

            except Exception as e:
                print(e)
                self.connected = False
                self.socket.close()
                break

    def send_message(self):
        # Obtener el mensaje ingresado en el cuadro de texto
        message = self.message_text.get('1.0', tk.END).strip()
        
        self.enable_log()

        # Verificar si estamos conectados al servidor
        if not self.connected:
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: no hay conexión con el servidor.')
            return

        # Verificar si el socket aún está abierto
        if not self.socket._closed:
            # Enviar el mensaje al servidor
            self.socket.sendall(message.encode())

            # Borrar el cuadro de texto de mensaje
            self.message_text.delete('1.0', tk.END)
        else:
            # Mostrar un mensaje de error si el socket está cerrado
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: la conexión con el servidor se ha perdido.')
        
        self.disable_log()

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    client_gui = ClientGUI(root)
    root.mainloop()