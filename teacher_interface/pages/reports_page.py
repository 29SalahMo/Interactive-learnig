import tkinter as tk
from tkinter import ttk
import json
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ReportsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        tk.Label(
            self,
            text="📑 Student Reports",
            font=("Arial", 24, "bold"),
            bg="white"
        ).pack(pady=20)

        # Load data
        data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
        self.students_path = os.path.join(data_folder, "students.json")
        self.results_path = os.path.join(data_folder, "quiz_results.json")

        self.students = self.load_json(self.students_path)
        self.results = self.load_json(self.results_path)

        # Dropdown for selecting student
        select_frame = tk.Frame(self, bg="white")
        select_frame.pack(pady=10)

        tk.Label(select_frame, text="Select Student:", font=("Arial", 14), bg="white").pack(side="left")

        student_names = [info["name"] for info in self.students.values()]
        self.student_ids = list(self.students.keys())

        self.selected_student = tk.StringVar()
        dropdown = ttk.Combobox(select_frame, textvariable=self.selected_student, values=student_names, state="readonly")
        dropdown.pack(side="left", padx=10)
        dropdown.bind("<<ComboboxSelected>>", self.update_report)

        # Report area (table + chart)
        self.table_frame = tk.Frame(self, bg="white")
        self.table_frame.pack(pady=20)

        self.chart_frame = tk.Frame(self, bg="white")
        self.chart_frame.pack(pady=10)

    def load_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}

    # -------------------------
    # STUDENT REPORT FUNCTIONS
    # -------------------------

    def update_report(self, event=None):
        """Update both table + chart when a student is selected."""

        # Clear previous table and chart
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        student_name = self.selected_student.get()
        
        # Find student ID
        student_id = None
        for sid, info in self.students.items():
            if info["name"] == student_name:
                student_id = sid
                break

        if not student_id:
            return

        # Get that student’s quiz results
        history = self.results.get(student_id, [])

        # Draw the table
        self.draw_table(history)

        # Draw progress chart
        self.draw_progress_chart(history)

    def draw_table(self, history):
        """Draws a table showing all quiz attempts."""

        columns = ("quiz", "score", "total")

        tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=6)
        tree.pack()

        tree.heading("quiz", text="Quiz Type")
        tree.heading("score", text="Score")
        tree.heading("total", text="Total")

        for attempt in history:
            tree.insert("", "end", values=(attempt["quiz"], attempt["score"], attempt["total"]))

    def draw_progress_chart(self, history):
        """Shows a line chart of the student’s progress over time."""

        if len(history) == 0:
            tk.Label(self.chart_frame, text="No quiz data available.", font=("Arial", 14), bg="white").pack()
            return

        scores = [attempt["score"] for attempt in history]
        attempts = list(range(1, len(history) + 1))

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(attempts, scores, marker="o", linestyle="-", color="#66a3ff")
        ax.set_title("Progress Over Time", fontsize=14)
        ax.set_xlabel("Attempt")
        ax.set_ylabel("Score")
        ax.set_ylim(0, 10)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
