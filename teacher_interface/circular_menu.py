import tkinter as tk
import math


class CircularMenu(tk.Canvas):
    def __init__(self, master, size=600, on_select=None):
        super().__init__(master, width=size, height=size, bg="white", highlightthickness=0)

        self.size = size
        self.center = size // 2
        self.radius = size // 2 - 20

        # Menu items (You can add more later)
        self.options = [
            "Student Scores",
            "Quiz Reports",
            "Manage Students",
            "Analytics",
            "Settings"
        ]

        self.selected_index = 0   # Current highlighted option
        self.on_select = on_select

        # Precompute number of slices
        self.slice_count = len(self.options)
        self.slice_angle = 360 / self.slice_count

        # Rotation of the whole wheel (in degrees).
        # You can tweak this to rotate everything.
        self.angle_offset = -72  # -90 would put one slice centered at the top

        # Draw the menu initially
        self.draw_menu()

    def draw_menu(self):
        """Draw circular slices + highlight the selected one."""
        self.delete("all")

        # Bounding box for the outer circle
        x0, y0 = 20, 20
        x1, y1 = self.size - 20, self.size - 20

        for i, label in enumerate(self.options):
            # ---- angles for this slice ----
            # where this slice starts (degrees, Tkinter uses 0° at 3 o'clock)
            start_angle = self.angle_offset + i * self.slice_angle
            extent = self.slice_angle

            # angle for the text = middle of the slice
            mid_angle_deg = start_angle + extent / 2

            # ---- color (highlight) ----
            color = "#66a3ff" if i == self.selected_index else "#cccccc"

            # ---- draw the slice ----
            self.create_arc(
                x0, y0, x1, y1,
                start=start_angle,
                extent=extent,
                fill=color,
                outline="black",
                width=2
            )

            # ---- place the text in the centre of the slice ----
            mid_angle = math.radians(mid_angle_deg)
            text_radius = self.radius * 0.6

            # IMPORTANT: y uses minus sin because screen y increases downward
            text_x = self.center + text_radius * math.cos(mid_angle)
            text_y = self.center - text_radius * math.sin(mid_angle)

            self.create_text(
                text_x, text_y,
                text=label,
                font=("Arial", 14, "bold"),
                fill="black"
            )

        # Optional inner circle to make a donut-style wheel
        inner_r = self.radius * 0.3
        self.create_oval(
            self.center - inner_r,
            self.center - inner_r,
            self.center + inner_r,
            self.center + inner_r,
            fill="white",
            outline="#dddddd"
        )

    def update_angle(self, angle):
        """
        Update the selected menu option based on rotation angle.
        Angle comes from C# TUIO marker rotation.
        """
        # Apply same offset so the slices and angles line up
        normalized = (angle - self.angle_offset) % 360

        # Determine which slice the angle falls into
        index = int(normalized // self.slice_angle)

        # Update only if selection changed
        if index != self.selected_index:
            self.selected_index = index
            print(f"[CIRCULAR MENU] Selected option: {self.options[index]}")
            self.draw_menu()

            # Trigger page change
            if self.on_select:
                self.on_select(self.options[index])
