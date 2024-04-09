    def add_client_button(self, client_name):
        # Create a Frame
        frame = tk.Frame(self.buttons_frame, bg='blue', padx=3, pady=3)

        # Create a Label for the square
        square = tk.Label(frame, text=' ', bg='green', width=2)
        square.pack(side='left')

        # Create a Button
        button = tk.Button(frame, text=client_name, width=10, height=1)
        button.bind('<Button-1>', lambda e: self.select_client(client_name))
        button.pack(side='right')

        # Add the Frame to the buttons_frame
        frame.pack()

        # Force Tkinter to update the frame's width
        frame.update_idletasks()

        # Calculate the width of the new frame
        frame_width = frame.winfo_reqwidth()

        # If this is the first frame or the width of the new frame plus the width of the frames in the current row exceeds the width of the canvas, start a new row
        if not self.client_buttons or frame_width + self.current_row_width > self.canvas_width: