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

        self.client_var = tk.StringVar()

        # Create a variable to store the selected client
        self.selected_client = 'Global'
        #self.is_private = False
        #self.selected_client = None

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(master, width=260, height=250, bg='blue')
        self.scrollbar = tk.Scrollbar(master, command=self.canvas.yview)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame to hold the buttons
        self.buttons_frame = tk.Frame(self.canvas, bg='blue')

        # Add the frame to the canvas
        self.canvas.create_window((0, 0), window=self.buttons_frame, anchor='nw')

        # Place the canvas and the scrollbar
        self.canvas.place(x=500, y=50)
        self.scrollbar.place(x=760, y=50, height=250)

        # Update the scroll region of the canvas when the buttons frame changes size
        self.buttons_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))


        # Create a "Global" button
        self.global_button = tk.Button(master, text='Global', state=tk.DISABLED, command=lambda: self.select_client('Global'))
        self.global_button.place_configure(x=600, y=15)

        # Create a "Remove Offline" button
        self.remove_offline_button = tk.Button(master, text='Eliminar\nDesconectados', command=self.remove_offline)
        self.remove_offline_button.place_configure(x=580, y=310)
        #self.remove_offline_button.pack()

        # Create a dictionary to store the client buttons
        self.client_buttons = {}

        # Estado del servidor
        self.status_label = tk.Label(master, text='Servidor detenido')
        #self.status_label.pack()
        self.status_label.place_configure(x=180, y=15) 
        self.log_text = tk.Text(master, height=10, width=50)
        self.log_text.config(state='disabled')
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

    def add_client_button(self, client_name):
        # Create a button for the client
        button = tk.Button(self.buttons_frame, text=client_name)

        # Bind a click event to the button
        button.bind('<Button-1>', lambda e: self.select_client(client_name))

        # Add the button to the frame
        button.pack()

        # Add the button to the client_buttons dictionary
        self.client_buttons[client_name] = button

    def select_client(self, client_name):
        #self.is_private = True
        # Set the selected client
        self.selected_client = client_name

    def update_client_dropdown(self):
        # Update client buttons
        for i, name in enumerate(self.connections.keys()):
            if name not in self.client_buttons:
                # Create a new button for the client
                self.add_client_button(name)

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
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    # Modify your handle_connection method
    def handle_connection(self, client_socket, client_address, client_name):
        name = client_name

        self.log(f'Cliente {name} conectado.')
        self.global_button.config(state='normal')  # Enable the 'Global' button

        self.enable_text
        self.log(f'El usuario: {name} se ha conectado')
        if name in self.client_buttons:
            self.client_buttons[name].config(bg='green')
        self.disable_text

        while True:
            try:  # Add try-except block for debugging
                data = client_socket.recv(1024)  # Se recibio tantos datos en como mensaje
            except Exception as e:
                print(f'Error receiving data: {e}')  # Debugging line
                break

            message = data.decode().strip()  # Los datos se vuelven bits

            if message == 'desconectado':
                self.client_buttons[name].config(bg='red')
                break

            if message == '':
                continue

            self.enable_text
            self.log(f'Datos de {name}: {message}')
            self.disable_text

            try:  # Add try-except block for debugging
                response = f'Datos enviados: {message}'.encode()
                client_socket.sendall(response)
            except Exception as e:
                print(f'Error sending data: {e}')  # Debugging line
                break

        client_socket.close()
        del self.connections[name]
        self.master.after(0, self.update_client_dropdown)  # Actualiza el menu de conectados
        self.enable_text
        self.log(f'Conexion cerrada con {name}')        
        self.disable_text
    
    def send_message(self):
        message = self.message_text.get('1.0', 'end').strip()
        self.message_text.delete('1.0', 'end')
        if message == '':
            return
        if self.global_button.config('relief')[-1] == 'sunken' or self.selected_client == 'Global':
            self.enable_text
            self.log(f'Mensaje global: {message}')
            # If the 'Global' button is pressed or the selected client is 'Global', send the message to all clients
            for client_socket in self.connections.values():
                self.disable_text
                message_aux = f'Mensaje global: {message}'
                client_socket.sendall(message_aux.encode())
        else:
            # If a client's button is pressed, send the message to that client only
            selected_client = self.selected_client
            if self.connections.get(selected_client):
                self.enable_text
                self.log(f'Mensaje a {selected_client}: {message}')
                message_aux = f'Mensaje privado: {message}'
                self.disable_text
                self.connections[selected_client].sendall(message_aux.encode())
            else:
                self.enable_text
                self.log(f'{selected_client} no está conectado')
                self.disable_text

    def disable_text(self):
        self.log_text.config(state='disabled')
    
    def enable_text(self):
        self.log_text.config(state='normal')

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
        self.enable_text
        self.log(f'Servidor corriendo en el puerto {PORT}')

        # Escuchar en el socket para conexiones entrantes
        self.server_socket.listen(1)

        self.connections = {}  
        self.disable_text

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