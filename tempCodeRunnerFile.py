ientes seleccionados
        
    def send_message(self):
        # Get the message entered in the text box
        message = self.message_text.get('1.0', tk.END).strip()

        # Check if we are connected to the server
        if not self.connected:
            messagebox.showerror('Error', 'No se pudo enviar el mensaje: no hay conexión con el servidor.')
            return

        # Split the message into sender, recipients, and the actual message
        parts = message.split('//')
        if len(parts) != 3:
            messagebox.showerror('Error', 'El formato del mensaje es incorrecto.')
            return

        sender = parts[0].split('-')[1]
        recipient