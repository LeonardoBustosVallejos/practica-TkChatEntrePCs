    def send_private_message(self, sender, message):
        print(f'send_private_message called with selected_clients={self.selected_clients}')  # Debug line
        for selected_client in self.selected_clients[:]: # Envia el mensaje a los clientes seleccionados
            if self.connections.get(selected_client):
                message_aux = f'Mensaje (Privado) de {sender}: {message}' # Muestra el mensaje en la ventana de log
                self.send_message_to_client(sender, selected_client, message_aux) # Envia el mensaje al cliente seleccionado
            else:
                self.handle_disconnected_client(selected_client)# Si el cliente no esta conectado
        # Log the message after all private messages have been sent
        recipients = " y ".join(self.selected_clients)
        self.log(f'Mensaje (Privado) de {sender} a {recipients}: {message}')