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
        # Etiqueta de nombre del servidor
        self.name = tk.StringVar()
        self.name.set("Pato")

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
    def remove_offline_button(self):
        # Eliminar los botones de los clientes desconectados
        for client_name in list(self.client_buttons.keys()):
            if client_name != 'Servidor' and client_name not in self.connected_clients:
                self.client_buttons[client_name].destroy()
                del self.client_buttons[client_name]

    def select_client(self, client_name):
        print(f"Client {client_name} selected.")
        # If 'Global' is selected, clear the list of selected clients
        # If 'Servidor' is selected, do nothing
        if client_name == 'Global':
            self.selected_clients = ['Global']
        else:
            # If 'Global' is in the list, remove it
            if 'Global' in self.selected_clients:
                self.selected_clients.remove('Global')
            # If the client is already in the list, remove it, otherwise, add it
            if client_name in self.selected_clients:
                self.selected_clients.remove(client_name)
            else:
                self.selected_clients.append(client_name)
        # If no client is selected, select 'Global' by default
        if not self.selected_clients:
            self.selected_clients = ['Global']
        # Update the recipients text box
        self.update_recipients_text()

    def update_recipients_text(self):
        # Enable the recipients text box
        self.messages_to_text.config(state='normal')
        # Clear the recipients text box
        self.messages_to_text.delete('1.0', tk.END)
        # Add the selected clients to the recipients text box
        self.messages_to_text.insert(tk.END, ', '.join(self.selected_clients))
        # Disable the recipients text box
        self.messages_to_text.config(state='disabled')
        print(f'selected_clients: {self.selected_clients}') # Linea de debug, se puede eliminar


    def on_close(self):
        self.disconnect_from_server()
        self.master.destroy()# Cerrar la ventana

    def receive_messages(self):
        while self.connected:
            try:
                # Receive data from the server
                data = self.socket.recv(1024).decode('utf-8')

                # If there's no data, the server closed the connection
                if not data:
                    self.log('Conexión perdida con el servidor')
                    self.disconnect_from_server()
                    break
                
                elif data.startswith('HIDDEN:'):
                    hidden_message = data[7:]
                    client_status_pairs = hidden_message.split(',')
                    print(f'client_status_pairs: {client_status_pairs}') # Debug line, can be removed
                    connected_clients = set()  # Create a set to store the clients received from the server
                    for pair in client_status_pairs:
                        if ':' in pair:  # Ignore empty strings
                            client, status = pair.split(':')
                            client = client.strip()  # Remove leading/trailing whitespace
                            status = status.strip()  # Remove leading/trailing whitespace
                            self.update_buttons(client, status)
                            connected_clients.add(client)  # Add the client to the set of received clients

                    # Find the clients that have disconnected
                    disconnected_clients = self.connected_clients - connected_clients
                    print(f'disconnected_clients: {disconnected_clients}') # Debug line, can be removed
                    for client in disconnected_clients:
                        self.update_buttons_colors(client, 'disconnected')  # Update the button color to red

                    self.connected_clients = connected_clients  # Update the set of connected clients

                # If the server sends 'SERVIDOR CAIDO...', disconnect
                elif data == 'SERVIDOR CAIDO...':
                    self.server_broken()
                    break

                # Check if the message is a response to a sent message
                elif data.startswith('RESPONSE'):
                    # Update the GUI with the response
                    self.update_sent_messages(data)

                else:
                    self.enable_log()
                    self.log_text.insert(tk.END, data + '\n')
                    self.log_text.see(tk.END)
                    self.disable_log()

            except Exception as e:
                print(e)
                self.connected = False
                self.socket.close()
                break

    def log_recipient(self, recipient):
        if not recipient:
            recipient = 'Global'
        self.messages_to_text.config(state='normal')
        self.messages_to_text.delete('1.0', 'end')
        self.messages_to_text.insert('end', recipient)
        self.messages_to_text.config(state='disabled')

    def server_broken(self):
        self.log('El servidor ha caído')
        self.disconnect_from_server()

    def update_buttons(self, client_name, status):
        # If the client is not in the list of buttons, add it
        if (client_name not in self.client_buttons) and (client_name != self.name.get()):
            try:
                # Create a button for the client
                button = self.create_button(client_name)
                button_width = button.winfo_reqwidth()  # Get the width of the button
                self.calculate_position(button_width)  # Calculate the position of the button
                self.add_button_to_grid_and_dict(button, client_name)  # Add the button to the grid and dictionary
                self.update_buttons_colors(client_name, status)  # Update the button color based on the client's status
                self.connected_clients.add(client_name)  # Add the client to the set of connected clients
            except Exception as e:
                print(f'Exception occurred: {e}') # Linea de debug, se puede eliminar
        else:
            self.update_buttons_colors(client_name, status) # Update the button color based on the client's status


    def create_button(self, client_name):
        button = tk.Button(self.buttons_frame, text=client_name, width=10, height=1)
        button.bind('<Button-1>', lambda e: self.select_client(client_name))
        button.update_idletasks()
        return button

    def calculate_position(self, button_width):
        if not self.client_buttons or button_width + self.current_row_width > self.canvas_width:
            self.current_row += 1
            self.current_row_width = 0
            self.current_column = 0
        else:
            self.current_column += 1
        self.current_row_width += button_width

    def add_button_to_grid_and_dict(self, button, client_name):
        button.grid(row=self.current_row, column=self.current_column, padx=3, pady=3)
        self.client_buttons[client_name] = button

    def update_buttons_colors(self, client_name, status):
        # Update the button state and color based on the client's status
        if client_name in self.client_buttons:
            if status == 'connected':
                self.client_buttons[client_name]['state'] = 'normal'
                self.client_buttons[client_name]['bg'] = 'green'
            elif status == 'disconnected':
                self.client_buttons[client_name]['state'] = 'disabled'
                self.client_buttons[client_name]['bg'] = 'red'


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

                self.log('Conectado al servidor')
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)
                self.global_button.config(state=tk.NORMAL)
                self.remove_offline_button.config(state=tk.NORMAL)
                # Change the background color of the server button to green
                self.client_buttons['Servidor'].config(bg='green')
                self.messages_to_text.config(state=tk.NORMAL)
                self.message_text.config(state=tk.NORMAL)
                self.send_button.config(state=tk.NORMAL)
                
                break  # Si se conectó, salir del bucle

            except Exception as e:
                print(e)

                # Configurar la variable de conexión
                self.connected = False

                # Esperar 5 segundos antes de intentar reconectar
                time.sleep(5)
                retries += 1
                if retries == max_retries:
                    self.log('No se pudo conectar al servidor después de varios intentos')
                    break

    def disconnect_from_server(self):
        # Enviar mensaje de desconexión al servidor
        if self.connected:
            self.socket.sendall('DISCONNECT'.encode())
        self.connected = False
        self.socket.close()
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

    def update_server_button_color(self):
        # Change the background color of the server button to red
        self.client_buttons['Servidor'].config(bg='red')

    def send_message(self):
        # Get the message from the text box
        message = self.message_text.get('1.0', tk.END).strip()
        self.enable_log()

        # Verify if we are connected to the server
        if not self.connected:
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: no hay conexión con el servidor.')
            return

        # Verify if the socket is still open
        if not self.socket._closed:
            # Send the message to the server
            message = f'SENDER-{self.name.get()}//CLIENTS_TO-{self.selected_clients}//MESSAGE.{message}'
            self.socket.sendall(message.encode())

            # Clear the message text box
            self.message_text.delete('1.0', tk.END)
        else:
            # Show an error message if the socket is closed
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: la conexión con el servidor se ha perdido.')
        
        self.disable_log()

    def listen_for_response(self):
        try:
            # Receive data from the server
            data = self.socket.recv(1024)
        except Exception as e:
            print(f'Error receiving data from the server: {e}')
            return None

        # Decode the data and return it
        return data.decode()

    def update_sent_messages(self, response):
        # Add the response to the GUI
        self.log('end', response + '\n')


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    client_gui = ClientGUI(root)
    root.mainloop()