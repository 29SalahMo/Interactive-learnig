import tkinter as tk

from socket_listener import SocketListener
from circular_menu import CircularMenu
from page_manager import PageManager

from pages.students_scores import StudentScoresPage
from pages.reports_page import ReportsPage
from pages.student_management import StudentManagementPage
from pages.analytics_page import AnalyticsPage
from pages.settings_page import SettingsPage


class TeacherApp:
    def __init__(self):
        # ----- Main window -----
        self.root = tk.Tk()
        self.root.title("Teacher Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")

        # ====== LAYOUT ======
        # Left: circular menu
        # Right: content pages

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True, fill="both")

        # Left side for menu
        menu_frame = tk.Frame(main_frame, bg="white")
        menu_frame.pack(side="left", fill="both", expand=False)

        # Right side for pages
        pages_frame = tk.Frame(main_frame, bg="white")
        pages_frame.pack(side="right", fill="both", expand=True)

        # ----- Page manager (this is where your two lines go) -----
        self.page_manager = PageManager(pages_frame)
        self.page_manager.pack(expand=True, fill="both")

        # ----- Circular menu -----
        # Note: CircularMenu now takes on_select= callback
        self.menu = CircularMenu(menu_frame, size=500, on_select=self.on_menu_select)
        self.menu.pack(expand=True, fill="both", padx=10, pady=10)

        # ----- Socket listener (Python TCP server) -----
        self.socket_server = SocketListener(
            host="localhost",
            port=5000,
            callback=self.on_angle_received
        )
        self.socket_server.start_server()

        # Start with a default page
        self.page_manager.show_page(StudentScoresPage)

        # UI update loop
        self.update_loop()

    # ========== SOCKET CALLBACK ==========
    def on_angle_received(self, angle: float):
        """
        Called whenever the C# system sends a rotation angle.
        We forward this to the circular menu to update selection.
        """
        print("[TEACHER APP] Updating rotation:", angle)
        self.menu.update_angle(angle)

    # ========== MENU SELECTION CALLBACK ==========
    def on_menu_select(self, option: str):
        """
        Called by CircularMenu whenever the selected option changes.
        We map option name -> page class and show that page.
        """
        print("[TEACHER APP] Opening page:", option)

        pages = {
            "Student Scores": StudentScoresPage,
            "Quiz Reports": ReportsPage,
            "Manage Students": StudentManagementPage,
            "Analytics": AnalyticsPage,
            "Settings": SettingsPage
        }

        page_class = pages.get(option)
        if page_class:
            self.page_manager.show_page(page_class)

    # ========== TKINTER LOOP ==========
    def update_loop(self):
        self.root.after(30, self.update_loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TeacherApp()
    app.run()
