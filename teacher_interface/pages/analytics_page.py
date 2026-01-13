import tkinter as tk
from tkinter import ttk
import json
import os
from statistics import mean

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class AnalyticsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        tk.Label(
            self,
            text="📈 Class Analytics",
            font=("Arial", 24, "bold"),
            bg="white"
        ).pack(pady=20)

        # Load student + quiz data
        data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
        self.students_path = os.path.join(data_folder, "students.json")
        self.results_path = os.path.join(data_folder, "quiz_results.json")

        self.students = self.load_json(self.students_path)
        self.results = self.load_json(self.results_path)

        # Frame for charts
        self.chart_frame = tk.Frame(self, bg="white")
        self.chart_frame.pack(pady=10)

        # Frame for heatmap table
        self.heatmap_frame = tk.Frame(self, bg="white")
        self.heatmap_frame.pack(pady=10)

        # Draw analytics
        self.draw_class_average_chart()
        self.draw_quiz_type_chart()
        self.draw_difficulty_heatmap()

    def load_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}

    # -----------------------
    #   CLASS AVERAGE SCORE
    # -----------------------
    def draw_class_average_chart(self):
        averages = []

        for student_id, attempts in self.results.items():
            if len(attempts) > 0:
                scores = [a["score"] for a in attempts]
                averages.append(mean(scores))

        if len(averages) == 0:
            tk.Label(self.chart_frame, text="No data available", bg="white").pack()
            return

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        ax.boxplot(averages, vert=True, patch_artist=True,
                   boxprops=dict(facecolor="#66a3ff"))

        ax.set_title("Class Score Distribution")
        ax.set_ylabel("Score")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # -------------------------
    #   SCORE BY QUIZ CATEGORY
    # -------------------------
    def draw_quiz_type_chart(self):
        quiz_categories = ["fruits", "animals", "shapes"]
        category_scores = {cat: [] for cat in quiz_categories}

        for student_id, attempts in self.results.items():
            for att in attempts:
                quiz = att.get("quiz")
                if quiz in category_scores:
                    category_scores[quiz].append(att["score"])

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        cats = quiz_categories
        avgs = [mean(category_scores[c]) if len(category_scores[c]) else 0 for c in cats]

        ax.bar(cats, avgs, color="#ffa64d")
        ax.set_title("Average Score by Quiz Type")
        ax.set_ylabel("Average Score")
        ax.set_ylim(0, 10)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

    # -------------------------
    #   HEATMAP (ITEM DIFFICULTY)
    # -------------------------
    def draw_difficulty_heatmap(self):
        """
        Counts mistakes for each item (apple, banana, cat, etc.)
        and displays them in a table colored by difficulty.
        """

        # Example reference items (should match your quiz items)
        quiz_items = [
            "apple", "banana", "orange",
            "cat", "dog", "elephant",
            "circle", "rectangle", "triangle"
        ]

        mistake_count = {item: 0 for item in quiz_items}

        # Count mistakes across all students
        for student_id, attempts in self.results.items():
            for att in attempts:
                # if real data includes mistake logs, replace this section later
                score = att["score"]
                total = att["total"]

                mistakes = total - score
                # Distribute mistakes evenly among items for demo purposes
                # (Until you integrate real mistake logs)
                if mistakes > 0:
                    share = mistakes / len(quiz_items)
                    for item in quiz_items:
                        mistake_count[item] += share

        # Draw heatmap table
        tk.Label(self.heatmap_frame, text="Item Difficulty Heatmap",
                 font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        for item, mistakes in mistake_count.items():
            # Color intensity based on mistakes
            red_intensity = min(255, int(mistakes * 30))
            color = f"#{red_intensity:02x}0000"

            row = tk.Frame(self.heatmap_frame, bg="white")
            row.pack(fill="x", pady=2)

            tk.Label(row, text=item.capitalize(), width=15, anchor="w",
                     font=("Arial", 12), bg="white").pack(side="left")

            tk.Label(row, text=f"{mistakes:.1f} mistakes",
                     font=("Arial", 12), bg=color, fg="white",
                     width=20).pack(side="left")
