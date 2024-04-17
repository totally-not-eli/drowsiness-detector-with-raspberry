import tkinter as tk
from tkinter import messagebox

MAX_DIGITS = 10  # Limit for additional digits

class UserInputWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enter Number")
        
        self.entry_field = tk.Entry(self.root, justify='right', width=15, font=('Arial', 24))
        self.initial_value = '+63'  # Define the prefix as a variable
        self.entry_field.insert(tk.END, self.initial_value)  # Set initial value to '+63'
        self.entry_field.grid(row=0, column=0, columnspan=3)
        
        btn_texts = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '*', '0', '⌫'  # Use '⌫' for backspace button
        ]
        
        row_val = 1
        col_val = 0
        
        for txt in btn_texts:
            cmd = lambda x=txt: self.press(x)
            tk.Button(self.root, text=txt, height=2, width=5, command=cmd).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 2:
                col_val = 0
                row_val += 1
        
        ok_button = tk.Button(self.root, text='OK', command=self.on_ok)
        ok_button.grid(row=row_val, column=1)

    def press(self, num):
        current = self.entry_field.get()
        if num == '⌫' and len(current) > len(self.initial_value):  # Allow backspace only if length is greater than the prefix
            self.entry_field.delete(len(current) - 1, tk.END)
        elif num != '⌫':
            if len(current.replace(self.initial_value, '')) < MAX_DIGITS:
                self.entry_field.insert(tk.END, num)

    def on_ok(self):
        user_number = self.entry_field.get().replace(self.initial_value, '')
        if len(user_number) == MAX_DIGITS:
            full_number = self.initial_value + user_number
            self.root.destroy()  # Close the window
            self.full_number = full_number 
        else:
            messagebox.showerror("Error", f"Please enter a 10 digit number after '+63'. Current length is {len(user_number)}.")

    def get_user_input(self):
        self.root.mainloop()
        return getattr(self, 'full_number', None)  # Return None if the full number was not set