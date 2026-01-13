import tkinter as tk
from tkinter import ttk
import json
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class StudentScoresPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        tk.Label(
            self,
            text="📊 Student Scores",
            font=("Arial", 24, "bold"),
            bg="white"
        ).pack(pady=20)

        # Load data
        data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
        students_path = os.path.join(data_folder, "students.json")
        results_path = os.path.join(data_folder, "quiz_results.json")

        self.students = self.load_json(students_path)
        self.results = self.load_json(results_path)

        # Draw chart
        self.draw_chart()

    def load_json(self, path):
        """Loads a JSON file safely."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}

    def draw_chart(self):
        """Draws a bar chart of the latest scores for each student."""
        # Prepare data
        names = []
        scores = []

        for student_id, info in self.students.items():
            name = info["name"]
            names.append(name)

            # Find latest score
            if student_id in self.results and len(self.results[student_id]) > 0:
                latest = self.results[student_id][-1]  # last quiz
                scores.append(latest["score"])
            else:
                scores.append(0)

        # Matplotlib figure
        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.bar(names, scores, color="#66a3ff")
        ax.set_title("Latest Quiz Scores", fontsize=16)
        ax.set_ylabel("Score")
        ax.set_ylim(0, 10)

        # Embed plot into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
