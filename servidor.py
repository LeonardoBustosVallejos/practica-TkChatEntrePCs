import socket
import threading
import tkinter as tk
import time

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
        self.name_label.place_configure(x=133, y = 15)

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
        self.send_button = tk.Button(master, text='Enviar', command=lambda: self.send_message(sender='Servidor', clients_to=self.selected_clients, message=None), state=tk.DISABLED)
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
        self.remove_offline_button = tk.Button(master, text='Eliminar\ndesconectados', command=self.remove_offline, state=tk.DISABLED)
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
        # Destinatarios
        self.recipients = ''
        # Lista de clientes inactivos
        self.inactive_clients = [] 
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
        elif isinstance(recipient, list):# Si el destinatario es una lista
            recipient = ', '.join(recipient)# Convierte la lista en una cadena de texto
        self.messages_to_text.config(state='normal')
        self.messages_to_text.delete('1.0', 'end')
        self.messages_to_text.insert('end', recipient)
        self.messages_to_text.config(state='disabled')
    
    def server_disconnected(self):
        self.name_label.config(bg='red')
        self.status_label.config(bg='red')

    def server_normal(self):
        self.name_label.config(bg='#f0f0f0')
        self.status_label.config(bg='#f0f0f0')
    
    # Habilita y deshabilita los botones cuando el servidor se inicia
    def enable_buttons(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.message_text.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.remove_offline_button.config(state=tk.NORMAL)

    # Habilita y deshabilita los botones cuando el servidor se detiene
    def disable_buttons(self):
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.remove_offline_button.config(state=tk.DISABLED)
            self.message_text.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)
            self.global_button.config(state=tk.DISABLED)
# =================================================================================================
# ==================================== FUNCIONES DEL SERVIDOR =====================================
    # Iniciar la conexión con el servidor
    def start_server(self):

        self.server_normal()
        self.enable_buttons() # Habilita los botones

        # Inicia el server
        self.server_running = True # Linea implementada para saber que el server esta corriendo
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

        # Muestra el estado del servidor en la ventana de status_label
        self.status_label.config(text='Iniciado')

        self.select_client('Global')# Selecciona el cliente global    
        self.log_recipient('Global')# Muestra los destinatarios en la ventana de messages_to_text

    # Servidor corriendo en un hilo separado para no bloquear la GUI
    def run_server(self):
        # Crear un objeto de socket TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Vincular el socket a una dirección y puerto específicos
        self.server_socket.bind((HOST, PORT))

        self.log(f'Servidor iniciado en el puerto {PORT}')

        # Escuchar en el socket para conexiones entrantes
        self.server_socket.listen(1)

        self.connections = {}  

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

        self.server_disconnected()
        self.disable_buttons()

        if self.server_running:
            # Detiene el server
            self.server_running = False # El server ya no esta corriendo
            self.send_system_message('SERVIDOR CAIDO...')

            time.sleep(1)  # Espera un segundo para que los mensajes se envíen antes de cerrar las conexiones

            for conn_dict in self.connections.values():
                try:
                    conn = conn_dict['connection']
                    conn.close()# Cierra la conexion con el cliente
                except Exception as e:
                    print(f'Error closing connection: {e}') # Linea de error

            try:
                self.server_socket.close()# Cierra conexion con el socket
            except Exception as e:
                print(f'Error closing socket: {e}') # Linea de error

            # Muestra el estado del servidor en la ventana de status_label
            self.status_label.config(text='detenido') 

        # Cierra la ventana si se presiono el boton de cerrar
        if close_gui:
            self.master.destroy()
# ===================================================================================================
    # ======================= BOTONES =======================
    def update_buttons_green(self, client_name):
        if client_name in self.client_buttons:
            self.client_buttons[client_name].config(bg='green')

    def update_buttons_yellow(self, client_name):
        if client_name in self.client_buttons:
            self.client_buttons[client_name].config(bg='yellow')

    def update_buttons_red(self, client_name):
        if client_name in self.client_buttons:
            self.client_buttons[client_name].config(bg='red')

    # Crear un botón para un cliente
    def create_button(self, client_name):
        button = tk.Button(self.buttons_frame, text=client_name, width=10, height=1)
        button.bind('<Button-1>', lambda e: self.select_client(client_name))
        button.update_idletasks()
        return button

        # actualizar el menu de conectados
    def update_client_buttons(self):
        # actualiza los clientes conectados
        for name in self.connections.keys():
            if name not in self.client_buttons:
                # Crea un boton para el cliente
                self.add_client_button(name)

    # Añadir un botón para un cliente
    def add_client_button(self, client_name):
        button = self.create_button(client_name)# Crea un botón para el cliente
        button_width = button.winfo_reqwidth()# Obtiene el ancho del botón
        self.calculate_position(button_width)# Calcula la posición del botón
        self.add_button_to_grid_and_dict(button, client_name)# Añade el botón al grid y al diccionario

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

    # Eliminar clientes desconectados
    def remove_offline(self):
        # Crea una copia de la lista de botones
        client_names = list(self.client_buttons.keys())
        # Itera sobre la lista de botones
        for name in client_names:
            if not self.connections.get(name):# Si el cliente no esta conectado
                self.client_buttons[name].destroy()# Remueve el botón
                del self.client_buttons[name]# Remueve el botón de la lista de botones

    # =================================================================================================
# ======================================= CONEXIONES ===============================================
    # Manejar la conexión con un cliente
    def handle_connection(self, client_socket, client_address, client_name):
        # añadir el cliente a la lista de conexiones
        self.connections[client_name] = {'connection': client_socket, 'connected': True}
        # Imprime el estado de todos los clientes
        self.print_client_status()
        self.initialize_connection(client_name)
        self.process_messages(client_socket, client_name)
        self.send_system_message(f'Cliente {client_name} se ha desconectado.')
        self.terminate_connection(client_socket, client_name)

    # Inicializar la conexión con el cliente
    def initialize_connection(self, client_name):
        self.send_system_message(f'Cliente {client_name} se ha conectado') # Muestra el mensaje en la ventana de log
        self.log(f'Cliente {client_name} se ha conectado.') # Muestra el mensaje en la ventana de log
        self.global_button.config(state='normal')  # Habilita el botón global cuando un cliente se conecta

        if client_name in self.client_buttons:
            print(f'Client {client_name} is in the client buttons') # Linea de error
        else:
            self.update_client_buttons(client_name)  # Actualiza el menu de conectados

        for client in self.connections.keys(): # Para cada cliente en la lista de conexiones
            if client not in self.inactive_clients: # Si el cliente no esta en la lista de clientes inactivos
                self.update_buttons_green(client) # Cambia el color del botón a verde
            else:
                self.update_buttons_yellow(client) # Cambia el color del botón a amarillo

    # Terminar la conexión con el cliente
    def terminate_connection(self, client_socket, client_name):
        client_socket.close() # Cierra la conexion con el cliente
        if client_name in self.connections:
            del self.connections[client_name]# Elimina la conexion del cliente
        self.master.after(0, self.update_client_buttons)  # Actualiza el menu de conectados
        self.log(f"Conexion cerrada con {client_name}")# Muestra el mensaje en la ventana de log 
        # Imprime el estado de todos los clientes
        self.print_client_status()

    # Desconectar un cliente
    def handle_disconnected_client(self, client):
        if client != 'Servidor':
            # El cliente pasa a estar desconectado
            self.connections[client]['connected'] = False 
            # Imprime el estado de todos los clientes
            self.print_client_status()
            self.remove_selected_client(client) 
            self.log_recipient(self.selected_clients)  # Muestra los destinatarios en la ventana de messages_to_text

    # Procesar los mensajes del cliente
    # Se relaciona tanto con mensajes como con la desconexión del cliente
    def process_messages(self, client_socket, client_name):
        while self.server_running:  # Solo procesa mensajes si el servidor esta corriendo
            try:
                message = self.receive_message(client_socket)  # Recibe el mensaje del cliente
                if message == 'DISCONNECT':  # Si el mensaje es 'DISCONNECT'
                    self.update_buttons_red(client_name)  # Cambia el color del botón a rojo

                    # Elimina el cliente de la lista de clientes inactivos
                    if client_name in self.inactive_clients:
                        self.inactive_clients.remove(client_name)  
                    break

                if message.startswith('ADVERTENCIA: '):
                    self.handle_parsed_message('Servidor', ['Global'], message)
                elif message != '':  # Si el mensaje no esta vacio
                    sender, clients_to, message_text = self.parse_message(message)  # Parsea el mensaje
                    self.handle_parsed_message(sender, clients_to, message_text)  # Maneja el mensaje parseado

                    if client_name in self.inactive_clients:  # Si el cliente esta en la lista de clientes inactivos
                        self.handle_reactived_client(client_name)  # Maneja el cliente inactivo

            # Maneja las excepciones
            except ConnectionAbortedError:  # Si la conexión fue abortada
                print(f'Connection with {client_name} was aborted.')  # Linea de error
            except Exception as e:  # Si hay un error
                print(f'Error processing messages from {client_name}: {e}')  # Linea de error

    def handle_inactive_client(self, client, message_text):
        # Si el cliente no esta en la lista de clientes inactivos
        if client not in self.inactive_clients: 
            self.inactive_clients.append(client)
            # Cambia el color del botón a amarillo
            self.update_buttons_yellow(client)
            # Muestra el mensaje en la ventana de log
            self.log(f"{message_text}") 
        else:
            # Muestra el mensaje en la ventana de log
            self.log(f'ADVERTENCIA: EL CLIENTE {client} SIGUE INACTIVO')
        # Muestra el mensaje en la ventana de log
        self.send_system_message(f'ADVERTENCIA: {client} ESTA INACTIVO')

    def handle_reactived_client(self, client):
        if client in self.inactive_clients:
            self.inactive_clients.remove(client)
            self.update_buttons_green(client)
            self.send_system_message(f'Cliente {client} ha vuelto a estar activo.')  # Muestra el mensaje en la ventana de log
            self.log(f'Sitema: Cliente {client} ha vuelto a estar activo.')  # Muestra el mensaje en la ventana de log
    # =================================================================================================
# =====================================================================================================

# ==================================== FUNCIONES DE LOS CLIENTES ======================================
    # ======================= SELECCIONAR CLIENTE =======================
    def select_client(self, client_name):

        if client_name == 'Global': # Si el cliente seleccionado es global
            self.selected_clients.clear() # Limpia la lista de clientes seleccionados
            self.selected_client = 'Global' # Selecciona el cliente global
            self.clients_to = '' # Asigna los clientes a los que se envio el mensaje a una cadena de texto vacia
        else:
            # Si el cliente esta en la lista de clientes seleccionados, elimínalo
            if client_name in self.selected_clients:
                self.selected_clients.remove(client_name)
            else:
                # Si el cliente no esta en la lista de clientes seleccionados, añadelo
                self.selected_clients.append(client_name)

            # SSi no hay clientes seleccionados, selecciona el cliente global
            if len(self.selected_clients) == 0:
                self.selected_client = 'Global'
            else:
                # Si hay clientes seleccionados, selecciona el primer cliente de la lista
                self.selected_client = self.selected_clients[0]

        # Muestra los destinatarios en la ventana de messages_to_text
        self.log_recipient(self.selected_clients)

    # Elimina el cliente de la lista de clientes seleccionados
    def remove_selected_client(self, client):
        self.selected_clients.remove(client)
# =================================================================================================
# ===================================== MENSAJES ======================================================
    def send_message(self, sender, clients_to, message=None):
        # Si no se es provisto un aargumento de mensaje, obtener el mensaje del campo de texto
        if message is None:
            message = self.message_text.get('1.0', 'end').strip()
            self.message_text.delete('1.0', 'end')

        # Si el mensaje esta vacio, no hacer nada
        if message == '':
            return
        
        # Si el remitente es el servidor
        if sender == 'Servidor':
            # Si 'Global' esta en la lista de clientes a los que se envio el mensaje
            if 'Global' in clients_to or not clients_to: 
                self.send_global_message(sender, message) # Envia un mensaje global
            # Si 'Global' no esta en la lista de clientes a los que se envio el mensaje
            elif 'Global' not in clients_to and clients_to: 
                self.send_private_message(sender, message) # Envia un mensaje privado
        # En cualquier otro caso
        else:
            # Si 'Global' esta en la lista de clientes a los que se envio el mensaje
            if 'Global' in clients_to:
                self.send_global_message(sender, message) # Envia un mensaje global
            else:
                self.send_private_message(sender, message) # Envia un mensaje privado

    # Recibe un mensaje del cliente
    def receive_message(self, client_socket):
        try:  # Agregar un bloque try-except para depuración
            data = client_socket.recv(1024)  # Se recibio tantos datos en como mensaje
        except Exception as e:
            print(f'Error receiving data: {e}')  # Linea de error
            return 'DISCONNECT'
        return data.decode().strip()  # Los datos se vuelven bits

    # Parsea el mensaje recibido del cliente
    def parse_message(self, message):
        parts = message.split('//') # Divide el mensaje en partes
        sender = parts[0].split('-')[1]# Obtiene el nombre del cliente que envio el mensaje
        clients_to = [client.strip("'") for client in parts[1].split('-')[1].strip('[]').split(', ')]# Obtiene los clientes a los que se envio el mensaje
        message_text = parts[2].split('.')[1]# Obtiene el texto del mensaje
        return sender, clients_to, message_text# Retorna el nombre del cliente que envio el mensaje, los clientes a los que se envio el mensaje y el texto del mensaje

    # Manejar los mensajes recibidos
    def handle_parsed_message(self, sender, clients_to, message_text):

        # i el mensaje comienza con 'ADVERTENCIA:' lo maneja separado
        if message_text.startswith('ADVERTENCIA:'):
            parts = message_text.split(' ')
            if len(parts) > 2:
                client = parts[1]
                self.handle_inactive_client(client, message_text)
            else:
                print("Warning message is not formatted correctly.")
            return

        clients_to_copy = clients_to.copy()  # Crea una copia de clients_to

        # Si 'Servidor' esta en la lista de clientes a los que se envio el mensaje
        if 'Servidor' in clients_to_copy:
            clients_to_copy.remove('Servidor')  # Remueve 'Servidor' de la lista de clientes a los que se envio el mensaje

        # Si 'Global' esta en la lista de clientes a los que se envio el mensaje
        if 'Global' in clients_to or '' in clients_to:
            self.send_global_message(sender, message_text)
        else:
            self.selected_clients = clients_to  # Asigna los clientes a los que se envio el mensaje a la lista de clientes seleccionados
            self.send_private_message(sender, message_text)  # Envia un mensaje privado
            recipients = " y ".join(self.selected_clients)  # Obtiene los destinatarios del mensaje como una cadena de texto separada por 'y'
            if sender != 'Servidor':  # Si el remitente no es el servidor
                self.log(f'{sender} (Privado) a {recipients}: {message_text}')  # Muestra el mensaje en la ventana de log
            # Asigna la copia de clients_to a la lista de clientes seleccionados
            # Con el fin de evitar que 'Servidor' esté dentro de los seleccionados
            self.selected_clients = clients_to_copy

    # Mensaje global
    def send_global_message(self, sender, message):
        for client_name, client_info in self.connections.items(): # Envia el mensaje a todos los clientes
            message_aux = f'{sender} (Global): {message}'# Mensaje global del remitente y el mensaje
            client_info['connection'].sendall(message_aux.encode()) # Envia el mensaje
        self.log(message_aux)# Muestra el mensaje en la ventana de log

    # Mensaje privado a un cliente específico
    def send_private_message(self, sender, message):
        for selected_client in self.selected_clients[:]: # Envia el mensaje a los clientes seleccionados
            if self.connections.get(selected_client): # Si el cliente esta conectado
                message_aux = f'{sender} (Privado): {message}' # Mensaje privado del remitente y el mensaje
                self.send_message_to_client(sender, selected_client, message_aux) # Envia el mensaje al cliente seleccionado
            else:
                self.handle_disconnected_client(selected_client)# Si el cliente no esta conectado

        self.send_response_to_sender(sender, self.selected_clients, message)# Envia una respuesta al remitente

    # Enviar un mensaje a un(unos) cliente(s) específico(s)
    def send_message_to_client(self, sender, client, message):
        try:
            self.connections[client]['connection'].sendall(message.encode())# Envia el mensaje al cliente seleccionado
        except Exception as e:
            self.log(f'Error sending message from {sender} to {client}: {e}')
            self.selected_clients.remove(client)# Elimina el cliente de la lista de clientes seleccionados

    # Enviar una respuesta al remitente
    def send_response_to_sender(self, sender, selected_clients, message):
        # Convierte la lista de clientes seleccionados en una cadena de texto
        selected_clients_str = ', '.join(selected_clients)

        #Enviando respuesta al remitente
        response = f'Privado a {selected_clients_str}: {message}' # Respuesta al remitente, los clientes seleccionados y el mensaje
        
        if sender == 'Servidor':# Si el remitente es el servidor
            self.log(f'Servidor (Privado) a {selected_clients_str}: {message}')
            pass
        else:
            # Envia la respuesta al remitente si no es el servidor
            self.connections[sender]['connection'].sendall(response.encode())

    # Imprimir el estado de los clientes
    def print_client_status(self):
        status_message = '' # Mensaje de estado de los clientes en blanco
        for client_name, client_info in self.connections.items():# Para cada cliente en la lista de conexiones
            status = 'connected' if client_info['connected'] else 'disconnected'# El cliente pasa a estar conectado si se encuentra en la lista de conexiones
            status_message += f'{client_name}: {status},\n' # Mensaje de estado de los clientes
        self.send_hidden_message_to_all(status_message) # Envia el mensaje oculto a todos los clientes
        self.send_inactive_clients_to_all() # Envia los clientes inactivos a todos los clientes

    # Enviar un mensaje a todos los clientes
    def send_hidden_message_to_all(self, message):
        for client_name, client_info in self.connections.items():
            if client_info['connected']:# Si el cliente esta conectado
                try:
                    client_info['connection'].sendall(('HIDDEN:' + message).encode())# Envia el mensaje al cliente + el mensaje oculto
                    print(f'Sent hidden message to {message}')# Muestra el mensaje en la ventana de log

                except Exception as e:
                    self.log(f'Error sending hidden message to {client_name}: {e}')
        
    def send_inactive_clients_to_all(self):
        inactive_clients = ', '.join(self.inactive_clients)
        message = f'INACTIVES:{inactive_clients}'
        for client_name, client_info in self.connections.items():
            if client_info['connected']:
                try:
                    client_info['connection'].sendall(message.encode())
                    time.sleep(0.1)
                except Exception as e:
                    self.log(f'Error sending inactive clients to {client_name}: {e}')

    # Enviar un mensaje a todos los clientes como el sistema
    def send_system_message(self, message, exclude_client=None):
        message_aux = f'Sistema: {message}' # Mensaje del sistema
        for client_name, client_info in list(self.connections.items()):  # Usa list() para evitar RuntimeError
            if client_name != exclude_client: # Si el cliente no es el excluido
                try:
                    self.disable_text()
                    client_info['connection'].sendall(message_aux.encode())  # Envia el mensaje al cliente que no fue excluido
                    self.enable_text()
                except ConnectionResetError:
                    # The client has disconnected abruptly
                    self.log(f'Cliente {client_name} se ha desconectado abruptamente.') # Muestra el mensaje en la ventana de log
                    # Remove the client from the connections dictionary
                    del self.connections[client_name] # Elimina la conexion del cliente
# =================================================================================================
root = tk.Tk()
server_gui = ServerGUI(root)
root.resizable(0,0)

root.mainloop()