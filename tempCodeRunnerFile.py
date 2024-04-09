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

    def add_client_button(self, client_name):
        button = self.create_button(client_name)
        button_width = button.winfo_reqwidth()
        self.calculate_position(button_width)
        self.add_button_to_grid_and_dict(button, client_name)
        def select_client(self, client_name):
            self.selected_client = client_name
            self.log_recipient(client_name)