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
        self.client_var = tk.StringVar()   # Variable para el nombre del cliente

# ======================================= IZQUIERDA DE LA GUI =======================================

        # Etiqueta de nombre del servidor
        self.name = tk.StringVar()
        self.name.set('Servidor')

        # Etiqueta de nombre del servidor
        self.name_label = tk.Label(master, textvariable=self.name)
        self.name_label.place_configure(x=130, y = 15)
        # Estado del servidor
        self.status_label = tk.Label(master, text='detenido')
        self.status_label.place_configure(x=180, y = 15) 
    
        # Texto para mostrar los mensajes
        self.log_text = tk.Text(master, height=10, width=50, state=tk.DISABLED)
        self.log_text.place_configure(x=20, y=50)

        # Iniciar el server
        self.start_button = tk.Button(master, text='Iniciar', command=self.start_server)
        self.start_button.place_configure(x=130, y=230)

        # Detener el server
        self.stop_button = tk.Button(master, text='Detener', command=self.stop_server, state=tk.DISABLED)
        self.stop_button.place_configure(x=230, y=230)

        # Texto de mensaje
        self.message_label = tk.Label(master, text='Mensaje:')
        self.message_label.place_configure(x=180, y = 265)

        # Texto para escribir los mensajes
        self.message_text = tk.Text(master, height=3, width=50)
        self.message_text.place_configure(x=20, y=290)

        # Boton para enviar mensajes
        self.send_button = tk.Button(master, text='Enviar', command=self.send_message, state=tk.DISABLED)
        self.send_button.place_configure(x=180, y=347)
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
        self.remove_offline_button = tk.Button(master, text='Eliminar\ndesconectados', command=self.remove_offline)
        self.remove_offline_button.place(x=510, y=280)

        # Destinatarios
        self.messages_to_label = tk.Label(master, text='Dirigido a:')
        self.messages_to_label.place(x=620, y=260)

        # Text para mostrar los destinatarios
        self.messages_to_text = tk.Text(master, bg='#f0f0f0', height = 4, width=18, state=tk.DISABLED)
        self.messages_to_text.place(x=620, y=280)
        
        # Insertar el nombre del cliente
        self.messages_to_text.insert('end', self.client_var)
# =================================================================================================

# ======================================= VARIABLES DE LA GUI =======================================
        # Servidor corriendo
        self.server_running = False
        # Botones de los clientes
        self.client_buttons = {}
        # Socket del cliente
        client_socket = None 
        # Guardar las conexiones
        self.connections = {
        }
        # clientes seleccionados para enviar mensajes
        self.selected_clients = []
# =================================================================================================

# ===================================== FUNCIONES UTILITARIAS =====================================
    
    # Habilitar y deshabilitar el log
    def enable_text(self):
        self.log_text.config(state='normal')

    def disable_text(self):
        self.log_text.config(state='disabled')

# La función log() se encarga de mostrar mensajes en la ventana de log_text.
    def log(self, message):
        self.enable_text()
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.disable_text()

# La función log_recipient() se encarga de mostrar los destinatarios en la ventana de messages_to_text.
    def log_recipient(self, recipient):
        if not recipient:
            recipient = 'Global'
        self.messages_to_text.config(state='normal')
        self.messages_to_text.delete('1.0', 'end')
        self.messages_to_text.insert('end', recipient)
        self.messages_to_text.config(state='disabled')
# =================================================================================================

# ==================================== FUNCIONES DEL SERVIDOR =====================================
    # Iniciar la conexión con el servidor
    def start_server(self):
        # Inicia el server
        self.server_running = True # Linea implementada para saber que el server esta corriendo
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.message_text.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)

        self.status_label.config(text='Iniciado')

        self.select_client('Global')# Selecciona el cliente global    
        self.log_recipient('Global')# Muestra los destinatarios en la ventana de messages_to_text

    # Servidor corriendo en un hilo separado para no bloquear la GUI
    def run_server(self):
        # Crear un objeto de socket TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Vincular el socket a una dirección y puerto específicos
        self.server_socket.bind((HOST, PORT))
        self.enable_text
        self.log(f'Servidor iniciado en el puerto {PORT}')

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
            self.update_client_buttons()  

            # Crear un hilo para manejar la conexión entrante
            t = threading.Thread(target=self.handle_connection, args=(conn, addr, name))
            t.start()

    # Detener la conexión con el servidor
    def stop_server(self, close_gui=False):
        if self.server_running:
            # Detiene el server
            self.server_running = False # El server ya no esta corriendo
            self.send_system_message('SERVIDOR CAIDO...')

            for conn in self.connections.values():
                try:
                    conn.close()# Cierra la conexion con el cliente
                except Exception as e:
                    print(f'Error closing connection: {e}')

            try:
                self.server_socket.close()# Cierra conexion con el socket
            except Exception as e:
                print(f'Error closing server socket: {e}')

            # Habilita y deshabilita los botones
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.message_text.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
            self.global_button.config(state=tk.DISABLED)

            self.status_label.config(text='detenido')

        # Cierra la ventana si se presiono el boton de cerrar
        if close_gui:
            self.master.destroy()
# =================================================================================================

# ==================================== FUNCIONES DE LOS CLIENTES ====================================
    # ======================= SELECCIONAR CLIENTE =======================
    def select_client(self, client_name):
        if client_name == 'Global':
            self.selected_clients.clear()
            self.selected_client = 'Global'
        else:
            # If the client is in the list of selected clients, remove it
            if client_name in self.selected_clients:
                self.selected_clients.remove(client_name)
            else:
                # If the client is not in the list of selected clients, add it
                self.selected_clients.append(client_name)

            # If there are no selected clients, select 'Global'
            if len(self.selected_clients) == 0:
                self.selected_client = 'Global'
            else:
                # If there are selected clients, select the first one in the list
                self.selected_client = self.selected_clients[0]

        self.log_recipient(self.selected_clients)
    # =================================================================================================

    # ======================= CONEXIONES =======================
    # actualizar el menu de conectados
    def update_client_buttons(self):
        # actualiza los clientes conectados
        for name in self.connections.keys():
            self.add_client_button_if_not_exists(name)

    def add_client_button_if_not_exists(self, name):
        if name not in self.client_buttons:
            # Crea un boton para el cliente
            self.add_client_button(name)

    # desconectar un cliente
    def handle_disconnected_client(self, client):
        # Set the 'connected' status of the client to False
        self.connections[client]['connected'] = False
        # Print the status of all clients
        self.print_client_status()  # Linea de depuración, se puede eliminar
        self.log(f'{client} no está conectado')
        self.remove_selected_client(client) 
        self.log_recipient(self.selected_clients)# Muestra los destinatarios en la ventana de messages_to_text

    def remove_selected_client(self, client):
        self.selected_clients.remove(client)# Elimina el cliente de la lista de clientes seleccionados

    # Manejar la conexión con un cliente
    def handle_connection(self, client_socket, client_address, client_name):
        # Add the new client to self.connections
        self.connections[client_name] = {'connection': client_socket, 'connected': True}
            # Print the status of all clients
        self.print_client_status()
        self.initialize_connection(client_name)
        self.process_messages(client_socket, client_name)
        self.send_system_message(f'Cliente {client_name} se ha desconectado.')
        self.terminate_connection(client_socket, client_name)

    def print_client_status(self):
        status_message = ''
        for client_name, client_info in self.connections.items():
            status = 'connected' if client_info['connected'] else 'disconnected'
            status_message += f'{client_name}: {status},\n'
        print(status_message)
        self.send_hidden_message_to_all(status_message)

    def send_hidden_message_to_all(self, message):
        for client_name, client_info in self.connections.items():
            if client_info['connected']:
                try:
                    client_info['connection'].sendall(('HIDDEN:' + message).encode())
                except Exception as e:
                    self.log(f'Error sending hidden message to {client_name}: {e}')

    def initialize_connection(self, client_name):
        self.send_system_message(f'Cliente {client_name} se ha conectado') # Muestra el mensaje en la ventana de log
        self.log(f'Cliente {client_name} se ha conectado.')
        self.global_button.config(state='normal')  # Habilita el botón global
        if client_name in self.client_buttons:
            self.client_buttons[client_name].config(bg='green') # Cambia el color del botón a verde
            
    def process_messages(self, client_socket, client_name):
        while self.server_running:
            if not self.connections[client_name]['connected']:
                break
            message = self.receive_message(client_socket)
            if message == 'DISCONNECT': # Si el mensaje es desconectar
                self.client_buttons[client_name].config(bg='red')# Cambia el color del botón a rojo
                break
            if message != '':
                self.log(f'Datos de {client_name}: {message}')# Muestra el mensaje en la ventana de log
                self.send_message(message)# Envia el mensaje a todos los clientes

    def terminate_connection(self, client_socket, client_name):
        client_socket.close() # Cierra la conexion con el cliente
        if client_name in self.connections:
            del self.connections[client_name]# Elimina la conexion del cliente
        self.master.after(0, self.update_client_buttons)  # Actualiza el menu de conectados
        self.log(f"Conexion cerrada con {client_name}")# Muestra el mensaje en la ventana de log 
        # Print the status of all clients
        self.print_client_status()
        
    def receive_message(self, client_socket):
        try:  # Agregar un bloque try-except para depuración
            data = client_socket.recv(1024)  # Se recibio tantos datos en como mensaje
        except Exception as e:
            print(f'Error receiving data: {e}')  # Linea de depuración, se puede eliminar
            return 'DISCONNECT'
        return data.decode().strip()  # Los datos se vuelven bits
    # =================================================================================================

    # ======================= BOTONES =======================
    # Crear un botón para un cliente
    def create_button(self, client_name):
        button = tk.Button(self.buttons_frame, text=client_name, width=10, height=1)
        button.bind('<Button-1>', lambda e: self.select_client(client_name))
        button.update_idletasks()
        return button

    # Calcular la posición de los botones
    def calculate_position(self, button_width):
        # Calcula la posición de los botones, si no hay espacio en la fila crea una nueva fila
        if not self.client_buttons or button_width + self.current_row_width > self.canvas_width:
            self.current_row += 1
            self.current_row_width = 0
            self.current_column = 0
        else:
            self.current_column += 1
        self.current_row_width += button_width

    # Añadir un botón al grid y al diccionario
    def add_button_to_grid_and_dict(self, button, client_name):
        # Coloca el botón en la fila y columna correspondiente
        button.grid(row=self.current_row, column=self.current_column, padx=3, pady=3)
        self.client_buttons[client_name] = button # Añade el botón al diccionario de botones

    # Añadir un botón para un cliente
    def add_client_button(self, client_name):
        button = self.create_button(client_name)# Crea un botón para el cliente
        button_width = button.winfo_reqwidth()# Obtiene el ancho del botón
        self.calculate_position(button_width)# Calcula la posición del botón
        self.add_button_to_grid_and_dict(button, client_name)# Añade el botón al grid y al diccionario

    # Eliminar clientes desconectados
    def remove_offline(self):
        # Create a copy of the keys
        client_names = list(self.client_buttons.keys())
        # Iterate over the copy
        for name in client_names:
            if not self.connections.get(name):# If the client is not connected
                self.client_buttons[name].destroy()# Remove the button
                del self.client_buttons[name]# Remove the button from the dictionary

    # =================================================================================================

    # ======================= ENVIAR MENSAJE =======================
# ======================= ENVIAR MENSAJE =======================
    def send_system_message(self, message, exclude_client=None):
        message_aux = f'Sistema: {message}'
        for client_name, client_info in list(self.connections.items()):  # Use list to avoid RuntimeError
            if client_name != exclude_client:
                try:
                    self.disable_text()
                    client_info['connection'].sendall(message_aux.encode())  # Send the message
                    self.enable_text()
                except ConnectionResetError:
                    # The client has disconnected abruptly
                    self.log(f'Cliente {client_name} se ha desconectado abruptamente.')
                    # Remove the client from the connections dictionary
                    del self.connections[client_name]

    # Mensaje global
    def send_global_message(self, message):
        for client_name, client_info in self.connections.items(): # Envia el mensaje a todos los clientes
            message_aux = f'Global: {message}'
            client_info['connection'].sendall(message_aux.encode()) # Envia el mensaje
        self.log(message_aux)# Muestra el mensaje en la ventana de log

    # Mensaje privado
    def send_private_message(self, message):
        for selected_client in self.selected_clients[:]: # Envia el mensaje a los clientes seleccionados
            if self.connections.get(selected_client):
                self.log(f'Mensaje a {selected_client}: {message}')
                message_aux = f'Mensaje privado: {message}' # Muestra el mensaje en la ventana de log
                self.send_message_to_client(selected_client, message_aux) # Envia el mensaje al cliente seleccionado
            else:
                self.handle_disconnected_client(selected_client)# Si el cliente no esta conectado

    # Enviar un mensaje a un(unos) cliente(s) específico(s)
    def send_message_to_client(self, client, message):
        try:
            self.connections[client]['connection'].sendall(message.encode())# Envia el mensaje al cliente
        except Exception as e:
            self.log(f'Error sending message to {client}: {e}')
            self.selected_clients.remove(client)# Elimina el cliente de la lista de clientes seleccionados
        
    def send_message(self, message=None):
        # If no message argument is provided, get the message from self.message_text
        if message is None:
            message = self.message_text.get('1.0', 'end').strip()
            self.message_text.delete('1.0', 'end')

        # If the message is empty, do nothing
        if message == '':
            return

        # If the selected client is 'Global', send the message to all clients
        if self.selected_client == 'Global':
            self.send_global_message(message)
        # If the selected client is not 'Global', send the message to the selected client
        else:
            self.send_private_message(message)
    #   =================================================================================================

root = tk.Tk()
server_gui = ServerGUI(root)
root.resizable(0,0)

root.mainloop()