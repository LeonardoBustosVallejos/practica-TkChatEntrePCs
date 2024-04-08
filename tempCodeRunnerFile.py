    def add_client_button(self, client_name):
        # Create a button for the client
        button = tk.Button(self.buttons_frame, text=client_name)

        # Bind a click event to the button
        button.bind('<Button-1>', lambda e: self.select_client(client_name))

        # Force Tkinter to update the button's width
        button.update_idletasks()

        # Calculate the width of the new button
        button_width = button.winfo_reqwidth()

        # If this is the first button or the width of the new button plus the width of the buttons in the current row exceeds the width of the canvas, start a new row
        if not self.client_buttons or button_width + self.current_row_width > self.canvas_width:
            self.current_row += 1
            self.current_row_width = 0
            self.current_column = 0  # Reset column index when a new row starts
        else:
            self.current_column += 1  # Increment column index for each new button within the same row

        # Add the button to the frame at the current row and the current column
        button.grid(row=self.current_row, column=self.current_column)

        # Add the button's width to the current row width
        self.current_row_width += button_width

        # Add the button to the client_buttons dictionary
        self.client_buttons[client_name] = button