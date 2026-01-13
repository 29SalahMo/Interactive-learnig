import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class StudentManagementPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        tk.Label(
            self,
            text="👤 Student Management",
            font=("Arial", 24, "bold"),
            bg="white"
        ).pack(pady=20)

        # Load data files
        data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
        self.students_path = os.path.join(data_folder, "students.json")
        self.results_path = os.path.join(data_folder, "quiz_results.json")

        self.students = self.load_json(self.students_path)
        self.results = self.load_json(self.results_path)

        # Layout frames
        self.table_frame = tk.Frame(self, bg="white")
        self.table_frame.pack(pady=10)

        self.controls_frame = tk.Frame(self, bg="white")
        self.controls_frame.pack(pady=10)

        # Draw student table
        self.draw_student_table()

        # Control buttons
        self.draw_controls()

    def load_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # -----------------------
    # TABLE OF STUDENTS
    # -----------------------
    def draw_student_table(self):
        """Displays the list of existing students."""

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        columns = ("id", "name")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=6)
        self.tree.pack()

        self.tree.heading("id", text="Student ID")
        self.tree.heading("name", text="Student Name")

        for sid, info in self.students.items():
            self.tree.insert("", "end", values=(sid, info["name"]))

    # -----------------------
    # CONTROL BUTTONS
    # -----------------------
    def draw_controls(self):
        """Below-table controls: add, edit, delete."""

        tk.Button(
            self.controls_frame,
            text="Add Student",
            font=("Arial", 12),
            command=self.add_student_window
        ).pack(side="left", padx=10)

        tk.Button(
            self.controls_frame,
            text="Edit Selected",
            font=("Arial", 12),
            command=self.edit_selected_student
        ).pack(side="left", padx=10)

        tk.Button(
            self.controls_frame,
            text="Delete Selected",
            font=("Arial", 12),
            command=self.delete_selected_student
        ).pack(side="left", padx=10)

    # -----------------------
    # ADD STUDENT
    # -----------------------
    def add_student_window(self):
        window = tk.Toplevel(self)
        window.title("Add Student")
        window.geometry("300x200")

        tk.Label(window, text="Student Name:", font=("Arial", 12)).pack(pady=10)
        name_entry = tk.Entry(window, font=("Arial", 12))
        name_entry.pack()

        def add():
            name = name_entry.get().strip()
            if name == "":
                messagebox.showerror("Error", "Name cannot be empty.")
                return

            # Generate a new student ID
            new_id = f"student{len(self.students) + 1:03d}"

            self.students[new_id] = {"name": name}
            self.results[new_id] = []

            self.save_json(self.students_path, self.students)
            self.save_json(self.results_path, self.results)

            self.draw_student_table()
            window.destroy()

        tk.Button(window, text="Add", font=("Arial", 12), command=add).pack(pady=10)

    # -----------------------
    # EDIT STUDENT
    # -----------------------
    def edit_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to edit.")
            return

        item = self.tree.item(selected)
        student_id, old_name = item["values"]

        window = tk.Toplevel(self)
        window.title("Edit Student")
        window.geometry("300x200")

        tk.Label(window, text="New Name:", font=("Arial", 12)).pack(pady=10)
        name_entry = tk.Entry(window, font=("Arial", 12))
        name_entry.insert(0, old_name)
        name_entry.pack()

        def save_edit():
            new_name = name_entry.get().strip()
            if new_name == "":
                messagebox.showerror("Error", "Name cannot be empty.")
                return

            self.students[student_id]["name"] = new_name
            self.save_json(self.students_path, self.students)

            self.draw_student_table()
            window.destroy()

        tk.Button(window, text="Save", font=("Arial", 12), command=save_edit).pack(pady=10)

    # -----------------------
    # DELETE STUDENT
    # -----------------------
    def delete_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete.")
            return

        item = self.tree.item(selected)
        student_id, name = item["values"]

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Remove student '{name}'?"):
            return

        del self.students[student_id]

        if student_id in self.results:
            del self.results[student_id]

        self.save_json(self.students_path, self.students)
        self.save_json(self.results_path, self.results)

        self.draw_student_table()
