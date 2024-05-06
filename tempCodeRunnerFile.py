    def add_button_to_grid_and_dict(self, button, client_name):
        button_color = 'green' if client_name not in self.inactive_clients else 'yellow'
        button.config(bg=button_color)
        button.grid(row=self.current_row, column=self.current_column, padx=3, pady=3) # Añade el botón al grid
        self.client_buttons[client_name] = button # Añade el botón al diccionario de botones