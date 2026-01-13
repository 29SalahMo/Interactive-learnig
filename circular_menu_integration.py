"""
Integration example: How to use CircularMenu with your main GUI application
This shows how to integrate the circular menu into your existing system
"""
import tkinter as tk
from circular_menu import CircularMenu, create_main_menu
import subprocess
import os
import sys


class CircularMenuApp:
    """Example integration of circular menu with main application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Circular Menu - TUIO Controlled")
        self.root.geometry("800x800")
        
        # Current user
        self.current_user = None
        
        # Processes
        self.quiz_process = None
        self.learning_process = None
        
        # Create menu with callbacks
        self.setup_menu()
    
    def setup_menu(self):
        """Setup the circular menu with callbacks"""
        callbacks = {
            'login': self.face_login,
            'signup': self.face_signup,
            'learning': self.start_learning_mode,
            'quiz': self.start_quiz_mode,
            'logout': self.logout
        }
        
        self.menu = create_main_menu(self.root, callbacks)
        
        # Add status label
        self.status_label = tk.Label(
            self.root,
            text="Place a TUIO marker on the menu to select an option",
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='white'
        )
        self.status_label.pack(pady=10)
    
    def face_login(self):
        """Handle face login"""
        try:
            from face_auth import FaceAuthManager
            auth = FaceAuthManager(camera_index=0)
            user_info = auth.login_child()
            
            if user_info:
                # Handle both dict and string return types
                if isinstance(user_info, dict):
                    user_name = user_info.get('name', 'Unknown')
                    user_gender = user_info.get('gender', 'Unknown')
                    self.current_user = user_name
                    self.status_label.config(
                        text=f"Logged in as: {user_name} ({user_gender})",
                        fg='#2ecc71'
                    )
                else:
                    # Fallback for old format
                    self.current_user = user_info
                    self.status_label.config(
                        text=f"Logged in as: {user_info}",
                        fg='#2ecc71'
                    )
            else:
                self.status_label.config(
                    text="Login failed or cancelled",
                    fg='#e74c3c'
                )
        except Exception as e:
            self.status_label.config(
                text=f"Login error: {str(e)}",
                fg='#e74c3c'
            )
    
    def face_signup(self):
        """Handle face signup"""
        from tkinter import simpledialog, messagebox
        name = simpledialog.askstring("Sign Up", "Enter child's name:")
        if not name:
            return
        
        # Ask for gender
        gender_window = tk.Toplevel(self.root)
        gender_window.title("Select Gender")
        gender_window.geometry("300x200")
        gender_window.configure(bg='#ecf0f1')
        gender_window.transient(self.root)
        gender_window.grab_set()
        
        selected_gender = {'value': 'boy'}  # Default
        
        def select_gender(gender):
            selected_gender['value'] = gender
            gender_window.destroy()
        
        tk.Label(
            gender_window,
            text="Please select the child's gender:",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=20)
        
        btn_frame = tk.Frame(gender_window, bg='#ecf0f1')
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="👦 Boy",
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='white',
            padx=30,
            pady=15,
            command=lambda: select_gender('boy'),
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="👧 Girl",
            font=('Arial', 14, 'bold'),
            bg='#ff69b4',
            fg='white',
            padx=30,
            pady=15,
            command=lambda: select_gender('girl'),
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        # Center the window
        gender_window.update_idletasks()
        x = (gender_window.winfo_screenwidth() // 2) - (gender_window.winfo_width() // 2)
        y = (gender_window.winfo_screenheight() // 2) - (gender_window.winfo_height() // 2)
        gender_window.geometry(f"+{x}+{y}")
        
        gender_window.wait_window()
        gender = selected_gender['value']
        
        try:
            from face_auth import FaceAuthManager
            auth = FaceAuthManager(camera_index=0)
            success = auth.register_child(name, gender)
            
            if success:
                gender_emoji = '👧' if gender.lower() == 'girl' else '👦'
                self.status_label.config(
                    text=f"Registration successful for {name} {gender_emoji}!",
                    fg='#2ecc71'
                )
            else:
                self.status_label.config(
                    text="Registration failed or cancelled",
                    fg='#e74c3c'
                )
        except Exception as e:
            self.status_label.config(
                text=f"Registration error: {str(e)}",
                fg='#e74c3c'
            )
    
    def start_learning_mode(self):
        """Start learning mode"""
        csharp_path = "TUIO11_NET-master/TUIO11_NET-master update/bin/Debug/TuioDemo.exe"
        
        if not os.path.exists(csharp_path):
            self.status_label.config(
                text="C# learning application not found!",
                fg='#e74c3c'
            )
            return
        
        try:
            exe_dir = os.path.dirname(csharp_path)
            self.learning_process = subprocess.Popen(
                [csharp_path],
                cwd=exe_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            self.status_label.config(
                text="Learning mode started! Place markers 0-8 on the table.",
                fg='#2ecc71'
            )
        except Exception as e:
            self.status_label.config(
                text=f"Failed to start learning mode: {str(e)}",
                fg='#e74c3c'
            )
    
    def start_quiz_mode(self):
        """Start quiz mode"""
        csharp_path = "TUIO11_NET-master/TUIO11_NET-master update/bin/Debug/TuioDemo.exe"
        hand_gesture_script = "stable_hand_recognition.py"
        
        if not os.path.exists(csharp_path):
            self.status_label.config(
                text="C# quiz application not found!",
                fg='#e74c3c'
            )
            return
        
        try:
            exe_dir = os.path.dirname(csharp_path)
            self.quiz_process = subprocess.Popen(
                [csharp_path],
                cwd=exe_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            # Start hand gesture recognition
            if os.path.exists(hand_gesture_script):
                subprocess.Popen(
                    [sys.executable, hand_gesture_script, "1"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                )
            
            self.status_label.config(
                text="Quiz mode started! Use hand gestures to answer questions.",
                fg='#2ecc71'
            )
        except Exception as e:
            self.status_label.config(
                text=f"Failed to start quiz mode: {str(e)}",
                fg='#e74c3c'
            )
    
    def logout(self):
        """Handle logout"""
        if self.current_user:
            self.current_user = None
            self.status_label.config(
                text="Logged out successfully",
                fg='#3498db'
            )
        else:
            self.status_label.config(
                text="You are not logged in",
                fg='#f39c12'
            )
    
    def on_closing(self):
        """Handle window closing"""
        if self.menu:
            self.menu.cleanup()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = CircularMenuApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

