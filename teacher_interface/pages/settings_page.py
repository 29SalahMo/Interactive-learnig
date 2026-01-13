import tkinter as tk

class SettingsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        tk.Label(
            self,
            text="⚙ Settings",
            font=("Arial", 24, "bold"),
            bg="white"
        ).pack(pady=40)
