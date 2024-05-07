import socket
import threading
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
        # Etiqueta de nombre del servidor
        self.name = tk.StringVar()
        self.name.set("CARBON")

        # Label para el nombre del usuario
        self.name_label = tk.Label(master, text='USUARIO: ')
        self.name_label.place(x=170, y=15)
        self.name_entry = tk.Label(master, textvariable=self.name)
        self.name_entry.place(x=230, y = 15)

        # Text para mostrar los mensajes
        self.log_text = tk.Text(master, height=10, width=50, state=tk.DISABLED)# Por default el text es de solo lectura
        self.log_text.place(x=20, y=50)

        # Conectar al server
        self.connect_button = tk.Button(master, text='Conectar', state=tk.DISABLED, command=self.connect_to_server)
        self.connect_button.place(x=130, y=230)

        # Desconectar del server
        self.disconnect_button = tk.Button(master, text='Desconectar', state=tk.NORMAL, command=self.disconnect_from_server)
        self.disconnect_button.place(x=230, y=230)
        
        # Texto de mensaje
        self.message_label = tk.Label(master, text='Mensaje:')
        self.message_label.place_configure(x=180, y = 265)

        # Text para escribir los mensajes
        self.message_text = tk.Text(master, height=3,width=50)
        self.message_text.place(x=20, y=290)

        self.send_button = tk.Button(master, text='Enviar', state = tk.NORMAL, command=self.send_message)
        self.send_button.place(x=180, y=347)
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
        self.current_column = 0  # Add this line
        self.canvas_width = 260 - 10

        # Configurar el evento de desplazamiento del canvas para que se ajuste al tamaño del frame
        self.buttons_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # Create a button for the server
        self.server_button = tk.Button(self.buttons_frame, text='Servidor', bg='green', width=10, height= 1, command=lambda: self.select_client('Servidor'))
        self.server_button.grid(row=0, column=0, padx=3, pady=3)
        # Add the server button to the dictionary of client buttons
        self.client_buttons = {'Servidor': self.server_button}

        # Boton "Eliminar desconectados"
        self.remove_offline_button = tk.Button(master, text='Eliminar\ndesconectados', command=self.remove_offline_button)
        self.remove_offline_button.place(x=510, y=280)

        # Destinatarios
        self.messages_to_label = tk.Label(master, text='Dirigido a:')
        self.messages_to_label.place(x=620, y=260)
        # Text para mostrar los destinatarios
        self.messages_to_text = tk.Text(master, bg='#f0f0f0', height = 4, width=18, state=tk.DISABLED)
        self.messages_to_text.place(x=620, y=280)

        self.log_recipient('Global')
# =================================================================================================

# ======================================= VARIABLES DE LA GUI =======================================
        # Variable para saber si esta conectado
        self.connected = False
        # Guardar clientes conectados
        self.connected_clients = set()
        # clientes seleccionados para enviar mensajes
        self.selected_clients = []
        # Conectar al servidor
        self.connect_to_server()
        # Considera si es la primera fila de botones
        self.first_row = True 
        # Lista de clientes inactivos
        self.innactive_clients = [] 
# ===================================================================================================

# ===================================== FUNCIONES UTILITARIAS =======================================
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
    # Agregar un destinatario a la caja de texto de log

    # Agregar un destinatario a la caja de texto de log
    def log_recipient(self, recipient):
        if recipient == '':
            recipient = 'Global'
        self.messages_to_text.config(state='normal')
        self.messages_to_text.delete('1.0', 'end')
        self.messages_to_text.insert('end', recipient)
        self.messages_to_text.config(state='disabled')

    # Actualizar el texto de los destinatarios, basado en los clientes seleccionados
    # Son 2 distintos métodos el log_recipient y el update_recipients_text
    # Motivo: Daba muchos errores de actualización de la GUI, asi que mejor dejarlo asi
    def update_recipients_text(self):
        self.messages_to_text.config(state='normal')
        self.messages_to_text.delete('1.0', tk.END)
        self.messages_to_text.insert(tk.END, ', '.join(self.selected_clients)) # Agregar los clientes seleccionados, separados por coma
        self.messages_to_text.config(state='disabled')
# ===================================================================================================

# ======================================= FUNCIONES DE CONEXIÓN =====================================
    # Función para conectarse al servidor
    def connect_to_server(self):
        max_retries = 3
        retries = 0
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

                # Inicia el temporizador de inactividad
                self.inactivity_timer = threading.Timer(10, self.send_warning)
                self.inactivity_timer.start()

                self.log('Conectado al servidor')
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)
                self.global_button.config(state=tk.NORMAL)
                self.remove_offline_button.config(state=tk.NORMAL)
                # Cambiar el color del botón del servidor a verde
                self.client_buttons['Servidor'].config(bg='green')
                self.messages_to_text.config(state=tk.NORMAL)
                self.message_text.config(state=tk.NORMAL)
                self.send_button.config(state=tk.NORMAL)
                
                break  # Si se conectó, salir del bucle

            except Exception as e:
                print(e) # Linea de excepción
                # Configurar la variable de conexión
                self.connected = False

                # Esperar 5 segundos antes de intentar reconectar
                time.sleep(5)
                retries += 1
                if retries == max_retries:
                    self.log('No se pudo conectar al servidor después de varios intentos')
                    break

    # Enviar una advertencia al servidor si el cliente está inactivo
    def send_warning(self):
        if self.connected:
            print('Sending warning')
            self.socket.sendall(f'ADVERTENCIA: {self.name.get()} ESTA INACTIVO'.encode('utf-8'))
            self.inactivity_timer = threading.Timer(60, self.send_warning)
            self.inactivity_timer.start()

    def reset_timer(self):
        if self.inactivity_timer is not None:
            self.inactivity_timer.cancel()
        self.inactivity_timer = threading.Timer(60, self.send_warning)
        self.inactivity_timer.start()

    # Función para manejar la desconexión del servidor
    def handle_server_disconnection(self):
        self.log('Conexión perdida con el servidor')
        self.disconnect_from_server()

    # Función para cerrar la ventana
    def on_close(self):
        self.disconnect_from_server()
        self.master.destroy()# Cerrar la ventana

    # Función para manejar la caída del servidor
    def server_broken(self):
        self.log('El servidor ha caído')
        self.disconnect_from_server()

    # Función para desconectarse del servidor
    def disconnect_from_server(self):
        try:
            # Enviar mensaje de desconexión al servidor
            if self.connected:
                try:
                    self.socket.sendall('DISCONNECT'.encode())
                except OSError:
                    print('Server already disconnected') # Linea de error
                self.socket.close()
        except (ConnectionResetError, ConnectionRefusedError):
            print('Error al desconectar del servidor') # Linea de error
        finally:
            self.connected = False
            self.log('Desconectado del servidor')
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.global_button.config(state=tk.DISABLED)
            self.remove_offline_button.config(state=tk.DISABLED)
            # Schedule the GUI update to run in the main thread
            self.master.after(0, self.update_server_button_color)
            self.messages_to_text.config(state=tk.DISABLED)
            self.message_text.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)

    def verify_inactive_clients(self, client):
        if client not in self.innactive_clients:
            self.innactive_clients.append(client)
        try:
            self.update_buttons_colors(client, 'inactive')
        except Exception as e:
            print(f'Exception occurred: {e}')

    def handle_reactived_clients(self, data):
        print(f'Data: {data}')  # Debug line
        parts = data.split(':')
        print(f'Parts: {parts}')  # Debug line
        client = ''  # Initialize client
        if len(parts) > 1:
            client = parts[1].strip().split(' ')[1]
            if client in self.innactive_clients:
                self.innactive_clients.remove(client)
                self.update_buttons_colors(client, 'connected')
                print(f'Cliente {client} reactivado')
                if client == self.name.get():
                    self.log('Sistema: YA NO ESTAS INACTIVO')
                else:
                    self.log(f'EL CLIENTE {client} YA NO ESTA INACTIVO')
        print(f'Self.innactive_clients: {self.innactive_clients}\nSelf.connected_clients: {self.connected_clients}\nClient: {client}')


        #if client == self.name.get():
        #    self.log('TE HAZ REACTIVADO')
        #elif self.innactive_clients is not None and client in self.connected_clients:
        #    self.log(f'EL CLIENTE {client} YA NO ESTA INACTIVO')
# ===================================================================================================

# ==================================== FUNCIONES DE CLIENTES ========================================
    # Función para seleccionar un cliente
    def select_client(self, client_name):

        if client_name == 'Global': # Si se selecciona Global, se seleccionan todos los clientes
            self.selected_clients = ['Global'] # Los clientes seleccionados sera 'Global'
        else:
            if 'Global' in self.selected_clients: # Si 'Global' esta en la lista de seleccionados, se elimina
                self.selected_clients.remove('Global')
            if client_name in self.selected_clients:
                self.selected_clients.remove(client_name) # Si el cliente ya esta en la lista, se elimina
            else:
                self.selected_clients.append(client_name) # Si no esta en la lista, se agrega
        if not self.selected_clients:
            self.selected_clients = ['Global']# Si no hay clientes seleccionados, se selecciona 'Global'

        self.update_recipients_text() # Actualizar el texto de los destinatarios

    # Función para actualizar los botones de los clientes desconectados
    def update_disconnected_clients(self, connected_clients):
        disconnected_clients = self.connected_clients - connected_clients# Clientes desconectados son los conectados actuales - los conectados almacenados
        for client in disconnected_clients: # Para cada cliente desconectado
            self.update_buttons_colors(client, 'disconnected') # Actualizar el color del botón a rojo

    # Función para obtener los clientes conectados
    def get_connected_clients(self, client_status_pairs):
        connected_clients = set() # Crear un conjunto vacio
        for pair in client_status_pairs: # Para cada par en la lista de pares
            if ':' in pair: # Si hay ':' en el par
                client, status = pair.split(':') # Separar el par en cliente y estado
                client = client.strip() # Eliminar espacios en blanco del cliente
                status = status.strip() # Eliminar espacios en blanco del estado
                self.update_buttons(client, status) # Actualizar los botones de los clientes con el cliente y el estado
                connected_clients.add(client) # Agregar el cliente al conjunto de clientes conectados

        return connected_clients # Regresar el conjunto de clientes conectados
# ===================================================================================================

# ======================================= BOTONES ===================================================
    # Función para crear un botón
    def create_button(self, client_name):
        button = tk.Button(self.buttons_frame, text=client_name, width=10, height=1) # Crear un botón con el nombre del cliente
        button.bind('<Button-1>', lambda e: self.select_client(client_name)) # Al hacer click izquierdo, se ejecuta la funcion select_client
        button.update_idletasks() # Actualizar el botón en la GUI

        return button # Regresar el botón

    # Eliminar los botones de los clientes desconectados
    def remove_offline_button(self):
        for client_name in list(self.client_buttons.keys()): # Para cada cliente en la lista de botones
            if client_name != 'Servidor' and client_name not in self.connected_clients: # Si el cliente no es 'Servidor' y no esta en la lista de clientes conectados
                self.client_buttons[client_name].destroy() # Eliminar el botón

                del self.client_buttons[client_name] # Eliminar el botón de la lista de botones

    # Función para actualizar los botones de los clientes
    def update_buttons(self, client_name, status):
        # Si el cliente no esta en la lista de botones y no es el cliente actual
        if (client_name not in self.client_buttons) and (client_name != self.name.get()):
            try:
                button = self.create_button(client_name) # Crear un botón con el nombre del cliente
                button_width = button.winfo_reqwidth()  # Obten el ancho del botón
                self.calculate_position(button_width)  # Calcula la posición del botón
                self.add_button_to_grid_and_dict(button, client_name)  # Añade el botón al grid y al diccionario
                self.update_buttons_colors(client_name, status)  # Actualiza el color del botón basado en el estado del cliente
                self.connected_clients.add(client_name)  # Añade el cliente a la lista de clientes conectados
            except Exception as e:
                print(f'Exception occurred: {e}') # Linea de excepción
        else:
            self.update_buttons_colors(client_name, status) # Actualiza el color del botón basado en el estado del cliente

    # Función para calcular la posición de los botones
    def calculate_position(self, button_width):
        if self.first_row:  # Si es la primera fila
            self.current_row_width = button_width  # Inicializa el ancho de la fila actual
            self.first_row = False  # Cambia el valor de la primera fila a False
        # Si no hay botones o el ancho del botón + el ancho de la fila actual es mayor al ancho del canvas
        if not self.client_buttons or button_width + self.current_row_width > self.canvas_width: 
            self.current_row += 1 # Aumenta el valor de la fila actual
            self.current_row_width = 0 # Inicializa el ancho de la fila actual
            self.current_column = 0 if self.current_row > 0 else 1 # Si la fila actual es mayor a 0, la columna actual es 0, si no, es 1
        else:
            self.current_column += 1 # Aumenta el valor de la columna actual
        self.current_row_width += button_width # Aumenta el ancho de la fila actual

    # Función para añadir un botón al grid y al diccionario
    def add_button_to_grid_and_dict(self, button, client_name):
        button.grid(row=self.current_row, column=self.current_column, padx=3, pady=3) # Añade el botón al grid
        self.client_buttons[client_name] = button # Añade el botón al diccionario de botones

    # Función para actualizar el color de los botones
    def update_server_button_color(self):
        self.client_buttons['Servidor'].config(bg='red') # Cambia el color del botón del servidor a rojo

    # Función para actualizar el color de los botones
    def update_buttons_colors(self, client_name, status): # Actualiza el color del botón basado en el estado del cliente
        if client_name in self.client_buttons: # Si el cliente esta en la lista de botones
            if status == 'connected': # Si el estado es conectado
                self.client_buttons[client_name]['state'] = 'normal' # Habilita el botón
                self.client_buttons[client_name]['bg'] = 'green' # Cambia el color del botón a verde
            elif status == 'disconnected': # Si el estado es desconectado
                self.client_buttons[client_name]['state'] = 'disabled' # Deshabilita el botón
                self.client_buttons[client_name]['bg'] = 'red' # Cambia el color del botón a rojo
            elif status == 'inactive': # Si el estado es inactivo
                self.client_buttons[client_name]['state'] = 'normal' # Habilita el botón
                self.client_buttons[client_name]['bg'] = 'yellow' # Cambia el color del botón a amarillo

    def reactivate_client(self, client):
        if client in self.innactive_clients:
            self.innactive_clients.remove(client)
        self.update_buttons_colors(client, 'connected')

# ===================================================================================================
# ====================================== MENSAJES ===================================================
    def send_message(self): # Función para enviar un mensaje
        message = self.message_text.get('1.0', tk.END).strip() # Obtiene el mensaje del text box
        self.enable_log()
        self.reset_timer() # Reinicia el temporizador de inactividad

        # Verifica si hay conexión con el servidor
        if not self.connected:
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: no hay conexión con el servidor.')
            return

        # Verificaa si el socket no esta cerrado
        if not self.socket._closed:
            # Enviar el mensaje al servidor
            message = f'SENDER-{self.name.get()}//CLIENTS_TO-{self.selected_clients}//MESSAGE.{message}' # Formato del mensaje
            self.socket.sendall(message.encode()) # Enviar el mensaje al servidor

            # Limpiar el text box
            self.message_text.delete('1.0', tk.END)
        else:
            # Muestra un mensaje de error si no se pudo enviar el mensaje
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: la conexión con el servidor se ha perdido.')
        
        self.disable_log()

    # Función para escuchar reespuestas
    def listen_for_response(self):
        try:
            # Revice datos del servidor
            data = self.socket.recv(1024)
        except Exception as e: # Si hay un error al recibir datos
            print(f'Error receiving data from the server: {e}') # Linea de excepción
            return None

        # Decodifica los datos recibidos y los regresa
        return data.decode()

    # Función para recibir mensajes
    def receive_messages(self):
        while self.connected: # Mientras este conectado
            try:
                data = self.socket.recv(1024).decode('utf-8') # Recibe datos del servidor
                
                # If the data starts with 'WARNING-', handle it separately
                if data.startswith('WARNING-'):
                    client = data.split('-')[1]
                    if client == self.name.get():
                        self.log(f'INACTIVE {client} DETECTED, SEND A MESSAGE')
                    else:
                        print(f'INACTIVE {client} DETECTED')
                    continue

                self.handle_received_data(data) # Maneja los datos recibidos
            except Exception as e:
                print(e) # Linea de excepción
                self.connected = False
                self.socket.close()
                break

    # Función para manejar los datos recibidos
    def handle_received_data(self, data):
        if not data: # Si no hay datos
            self.handle_server_disconnection() # Maneja la desconexión del servidor
        elif data.startswith('HIDDEN:'): # Si los datos empiezan con 'HIDDEN:'
            self.handle_hidden_message(data[7:]) # Maneja los mensajes ocultos
        elif data == 'Sistema: SERVIDOR CAIDO...': # Si los datos son 'Sistema: SERVIDOR CAIDO...'
            self.server_broken() # Maneja la caída del servidor
        elif data.startswith('RESPONSE'): # Si los datos empiezan con 'RESPONSE'
            self.update_sent_messages(data) # Actualiza los mensajes enviados
        elif data.startswith('Sistema: ADVERTENCIA:'): # Si los datos empiezan con 'MESSAGE'
            self.handle_inactive_clients(data) # Agrega los datos a la caja de texto de log
        elif data.startswith('Sistema: Cliente'): # Si los datos empiezan con 'MESSAGE'   
            self.handle_reactived_clients(data) # Agrega los datos a la caja de texto de log
        else: # En cualquier otro caso
            self.log(data) # Agrega los datos a la caja de texto de log

    # Función para manejar los mensajes ocultos
    def handle_hidden_message(self, hidden_message):
        client_status_pairs = hidden_message.split(',') # Divide los mensajes ocultos en pares de cliente y estado
        connected_clients = self.get_connected_clients(client_status_pairs) # Obtiene los clientes conectados
        self.update_disconnected_clients(connected_clients) # Actualiza los clientes desconectados
        self.connected_clients = connected_clients # Actualiza la lista de clientes conectados

    # Función para actualizar los mensajes enviados
    def update_sent_messages(self, response):
        self.log('end', response + '\n') # Agrega los mensajes enviados a la caja de texto de log

    def handle_inactive_clients(self, data):
        parts = data.split(':')
        if len(parts) > 2:
            client = parts[2].strip().split(' ')[0]  # Get the client's name
            if client == self.name.get():  
                if client in self.innactive_clients:
                    self.log('ADVERTENCIA: SIGUES ESTANDO INACTIVO')
                else:
                    self.log('ADVERTENCIA: ESTAS INACTIVO') 
            else:
                self.log(f"EL CLIENTE {client} ESTA INACTIVO")
        else:
            self.log("El mensaje no esta en el formato correcto")

        self.verify_inactive_clients(client)
# ====================================================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    client_gui = ClientGUI(root)
    root.mainloop()