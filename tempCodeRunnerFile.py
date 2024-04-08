    def add_client_button(self, client_name):
        button_width = 100
        button_height = 30
        canvas_width = self.buttons_frame.winfo_width()

        if self.x + button_width > canvas_width:
            self.x = 0
            self.y += button_height

        # Create a button for the client
        button = tk.Button(self.buttons_frame, text=client_name)

        # Bind a click event to the button
        button.bind('<Button-1>', lambda e: self.select_client(client_name))

        # Add the button to the frame at the specified position
        button.place(x=self.x, y=self.y, width=button_width, height=button_height)

        self.x += button_width

        # Add the button to the client_buttons dictionary
        self.client_buttons[client_name] = button