import tkinter as tk

class PageManager(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.current_page = None

    def show_page(self, page_class):
        """Destroys current page and loads a new page."""
        if self.current_page is not None:
            self.current_page.destroy()

        self.current_page = page_class(self)
        self.current_page.pack(expand=True, fill="both")
