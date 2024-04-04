import socket
import threading
import tkinter as tk

HOST = ''  # Significa que escucha en todas las interfaces de red
PORT = 8888  # Puerto para escuchar
MAX_CONNECTIONS = 1000000  # Número máximo de conexiones simultáneas

class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title('Servidor')
        master.resizable(0,0)
        master.geometry('800x380')
        master.protocol("WM_DELETE_WINDOW", lambda: self.stop_server(close_gui=True))# Al cerrar la ventana se detiene el server

        # Create a frame for new connections
        self.new_connections_frame = tk.Frame(master, width=260, height=250)  # Increase the width of the frame
        self.new_connections_frame.config(bg='blue')
        #self.new_connections_frame.pack()
        self.new_connections_frame.place_configure(x=500, y=50)

        # Create a "Global" button
        self.global_button = tk.Button(self.new_connections_frame, text='Global', command=self.send_message)
        self.global_button.pack()
        self.global_button.place_configure(x=10, y=10)

        # Create a "Remove Offline" button
        self.remove_offline_button = tk.Button(self.new_connections_frame, text='Eliminar\nDesconectados', command=self.remove_offline)
        self.remove_offline_button.place_configure(x=30, y=30)
        #self.remove_offline_button.pack()

        # Create a dictionary to store the client buttons
        self.client_buttons = {}

        # Estado del servidor
        self.status_label = tk.Label(master, text='Servidor detenido')
        #self.status_label.pack()
        self.status_label.place_configure(x=180, y=15) 
        self.log_text = tk.Text(master, height=10, width=50)
        self.log_text.config(state= 'disabled')
        #self.log_text.pack()
        self.log_text.place_configure(x=20, y=50)

        # Iniciar el server
        self.start_button = tk.Button(master, text='Iniciar', command=self.start_server)
        #self.start_button.pack()
        self.start_button.place_configure(x=130, y=230)

        # Detener el server
        self.stop_button = tk.Button(master, text='Detener', command=self.stop_server, state=tk.DISABLED)
        #self.stop_button.pack()
        self.stop_button.place_configure(x=230, y=230)

        # Texto para mensajes
        self.message_text = tk.Text(master, height=3, width=50)
        #self.message_text.pack()
        self.message_text.place_configure(x=20, y=270)

        # Boton para enviar mensajes
        self.send_button = tk.Button(master, text='Enviar', command=self.send_message, state=tk.DISABLED)
        #self.send_button.pack()
        self.send_button.place_configure(x=180, y=330)

        # Servidor corriendo
        self.server_running = False
        # Guardar las conexiones
        self.connections = {}

    # Actualizar Menu de conectados
    def update_client_dropdown(self):
        # Update client buttons
        for name in self.connections.keys():
            if name not in self.client_buttons:
                # Create a new button for the client
                button = tk.Button(self.new_connections_frame, text=name, command=lambda value=name: self.send_message(value))
                #button.pack()
                button.place_configure(x=0, y=0)
                self.client_buttons[name] = button

    def start_server(self):
        # Inicia el server
        self.server_running = True # Linea implementada para saber que el server esta corriendo
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.message_text.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)

        self.status_label.config(text='Servidor corriendo')

    def stop_server(self, close_gui=False):
        if self.server_running:
            # Detiene el server
            self.server_running = False # El server ya no esta corriendo

            for conn in self.connections.values():
                conn.close()

            self.server_socket.close()

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.message_text.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)

            self.status_label.config(text='Servidor detenido')

        # Cierra la ventana si se presiono el boton de cerrar
        if close_gui:
            self.master.destroy()


    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def handle_connection(self, conn, addr, name):
        self.log_text.config(state= 'normal')
        self.log(f'El usuario: {name} se ha conectado')
        self.client_buttons[name].config(bg='green')
        self.log_text.config(state= 'disabled')

        while True:
            # Recibir los datos enviados por el cliente
            data = conn.recv(1024)  # Se recibio tantos datos en como mensaje
            message = data.decode().strip()  # Los datos se vuelven bits

            if message == 'desconectado':
                # El cliente se ha desconectado
                break

            if message == '':
                # Ignorar mensajes vacíos
                continue

            # Datos recibido por el usuario conectado al server
            self.log_text.config(state= 'normal')
            self.log(f'Datos de {name}: {message}')
            self.log_text.config(state= 'disabled')

            # Lo que ve el cliente
            response = f'Datos enviados: {message}'.encode()

            conn.sendall(response)

        # Cerrar la conexión
        conn.close()
        del self.connections[name]
        self.master.after(0, self.update_client_dropdown)  # Actualiza el menu de conectados
        self.log_text.config(state= 'normal')
        self.log(f'Conexion cerrada con {name}')        
        self.log_text.config(state= 'disabled')
        
    def send_message(self):
        self.log_text.config(state= 'normal')
        message = self.message_text.get(1.0, tk.END).strip()
        self.message_text.delete(1.0, tk.END)
        recipient = self.client_var.get()

        if recipient == 'Global':
            self.log(f'Mensaje Global: {message}')
            message = f'Mensaje recibido: {message}'
            for conn in self.connections.values():
                conn.sendall(message.encode())
        else:
            self.log(f'Mensaje a {recipient}: {message}')
            conn = self.connections.get(recipient)
            if conn:
                message = f'Mensaje recibido: {message}'
                conn.sendall(message.encode())
        self.log_text.config(state= 'disabled')

    def remove_offline(self):
        # Remove all offline clients from the list of client buttons
        for name, button in list(self.client_buttons.items()):
            if not self.connections.get(name):
                button.destroy()
                del self.client_buttons[name]

    def run_server(self):
        # Crear un objeto de socket TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Vincular el socket a una dirección y puerto específicos
        self.server_socket.bind((HOST, PORT))
        self.log_text.config(state= 'normal')
        self.log(f'Servidor corriendo en el puerto {PORT}')

        # Escuchar en el socket para conexiones entrantes
        self.server_socket.listen(1)

        self.connections = {}  
        self.log_text.config(state= 'disabled')

        # Ciclo infinito para manejar conexiones entrantes
        while self.server_running:
            try:
                # Aceptar una conexión entrante
                conn, addr = self.server_socket.accept()
            except OSError:
                break

            # Recibir el nombre del cliente
            data = conn.recv(1024)
            name = data.decode().strip()
            self.connections[name] = conn  # Guarda la direccion bajo el nombre del cliente
            self.update_client_dropdown()  

            # Crear un hilo para manejar la conexión entrante
            t = threading.Thread(target=self.handle_connection, args=(conn, addr, name))
            t.start()

root = tk.Tk()
server_gui = ServerGUI(root)
root.resizable(0,0)

root.mainloop()