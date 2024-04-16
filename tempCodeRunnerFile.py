    def remove_offline(self):
        # Create a copy of the keys
        client_names = list(self.client_buttons.keys())
        # Iterate over the copy
        for name in client_names:
            if not self.connections.get(name):# If the client is not connected
                self.client_buttons[name].destroy()# Remove the button
                del self.client_buttons[name]# Remove the button from the dictionary