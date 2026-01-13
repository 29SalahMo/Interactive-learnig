"""
Main GUI Application for Interactive English Learning Quiz System
Integrates Login/Signup, Learning Mode, and Quiz Mode
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import os
import sys
import threading
import socket
import json
import time

try:
    from face_auth import FaceAuthManager
    FACE_AUTH_AVAILABLE = True
except ImportError as e:
    FACE_AUTH_AVAILABLE = False
    print(f"Warning: Face authentication not available: {e}")

try:
    from circular_menu import create_main_menu
    CIRCULAR_MENU_AVAILABLE = True
except ImportError as e:
    CIRCULAR_MENU_AVAILABLE = False
    print(f"Warning: Circular menu not available: {e}")


class MainApplication:
    """Main GUI application for the learning system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive English Learning Quiz System")
        self.root.geometry("900x700")
        
        # Current user
        self.current_user = None
        self.current_user_gender = None
        
        # Theme colors
        self.themes = {
            'boy': {
                'bg_main': '#2c3e50',
                'bg_header': '#34495e',
                'bg_frame': '#34495e',
                'bg_button': '#3498db',  # Blue
                'bg_button_secondary': '#2980b9',  # Darker blue
                'bg_user': '#ecf0f1',
                'accent': '#3498db',  # Blue accent
                'success': '#2ecc71',
                'title': '🎓 Interactive English Learning Quiz'
            },
            'girl': {
                'bg_main': '#ffe4e1',  # Misty rose (pink background)
                'bg_header': '#ff69b4',  # Hot pink header
                'bg_frame': '#ffb6c1',  # Light pink frames
                'bg_button': '#ff1493',  # Deep pink buttons
                'bg_button_secondary': '#ff69b4',  # Hot pink
                'bg_user': '#fff0f5',  # Lavender blush
                'accent': '#ff1493',  # Deep pink accent
                'success': '#ff69b4',  # Pink success
                'title': '💕 Interactive English Learning Quiz'
            }
        }
        self.current_theme = self.themes['boy']  # Default theme
        
        # Set initial background
        self.root.configure(bg=self.current_theme['bg_main'])
        
        # Processes for sub-applications
        self.quiz_process = None
        self.hand_gesture_process = None
        self.learning_process = None
        
        # Circular menu window
        self.circular_menu_window = None
        self.circular_menu = None
        
        # Socket connection
        self.socket_client = None
        self.socket_host = 'localhost'
        self.socket_port = 8888
        
        # Socket server for receiving login updates from external scripts
        self.login_socket_server = None
        self.login_socket_port = 8889
        self.setup_login_socket_server()
        
        # Setup UI
        self.setup_ui()
        
        # Check for C# app
        self.check_csharp_app()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        self.header_frame = tk.Frame(self.root, bg=self.current_theme['bg_header'], height=100)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        self.header_frame.pack_propagate(False)
        
        self.title_label = tk.Label(
            self.header_frame,
            text=self.current_theme['title'],
            font=('Arial', 24, 'bold'),
            bg=self.current_theme['bg_header'],
            fg='white'
        )
        self.title_label.pack(pady=20)
        
        # User info frame
        self.user_frame = tk.Frame(self.root, bg=self.current_theme['bg_user'], relief=tk.RAISED, bd=2)
        self.user_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.user_label = tk.Label(
            self.user_frame,
            text="Not logged in",
            font=('Arial', 12),
            bg=self.current_theme['bg_user'],
            fg='#7f8c8d'
        )
        self.user_label.pack(pady=10)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, bg=self.current_theme['bg_main'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login/Signup section
        self.auth_frame = tk.LabelFrame(
            self.content_frame,
            text="Login / Sign Up",
            font=('Arial', 14, 'bold'),
            bg=self.current_theme['bg_frame'],
            fg='white',
            padx=20,
            pady=15
        )
        self.auth_frame.pack(fill=tk.X, pady=10)
        
        self.btn_frame_auth = tk.Frame(self.auth_frame, bg=self.current_theme['bg_frame'])
        self.btn_frame_auth.pack(pady=10)
        
        self.login_btn = tk.Button(
            self.btn_frame_auth,
            text="🔐 Face Login",
            font=('Arial', 12, 'bold'),
            bg=self.current_theme['bg_button'],
            fg='white',
            padx=20,
            pady=10,
            command=self.face_login,
            cursor='hand2'
        )
        self.login_btn.pack(side=tk.LEFT, padx=10)
        
        self.signup_btn = tk.Button(
            self.btn_frame_auth,
            text="➕ Sign Up",
            font=('Arial', 12, 'bold'),
            bg=self.current_theme['success'],
            fg='white',
            padx=20,
            pady=10,
            command=self.face_signup,
            cursor='hand2'
        )
        self.signup_btn.pack(side=tk.LEFT, padx=10)
        
        self.logout_btn = tk.Button(
            self.btn_frame_auth,
            text="🚪 Logout",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            command=self.logout,
            cursor='hand2'
        )
        self.logout_btn.pack(side=tk.LEFT, padx=10)
        
        # Learning Mode section
        self.learning_frame = tk.LabelFrame(
            self.content_frame,
            text="Learning Mode",
            font=('Arial', 14, 'bold'),
            bg=self.current_theme['bg_frame'],
            fg='white',
            padx=20,
            pady=15
        )
        self.learning_frame.pack(fill=tk.X, pady=10)
        
        self.learning_desc = tk.Label(
            self.learning_frame,
            text="Learn English words with interactive markers!\nPlace markers 0-8 on the table to see images, hear sounds, and learn words.",
            font=('Arial', 10),
            bg=self.current_theme['bg_frame'],
            fg='white',
            justify=tk.LEFT
        )
        self.learning_desc.pack(pady=5)
        
        self.learning_btn = tk.Button(
            self.learning_frame,
            text="📚 Start Learning Mode",
            font=('Arial', 12, 'bold'),
            bg='#9b59b6',
            fg='white',
            padx=20,
            pady=10,
            command=self.start_learning_mode,
            cursor='hand2'
        )
        self.learning_btn.pack(pady=10)
        
        # Quiz Mode section
        self.quiz_frame = tk.LabelFrame(
            self.content_frame,
            text="Quiz Mode",
            font=('Arial', 14, 'bold'),
            bg=self.current_theme['bg_frame'],
            fg='white',
            padx=20,
            pady=15
        )
        self.quiz_frame.pack(fill=tk.X, pady=10)
        
        self.quiz_desc = tk.Label(
            self.quiz_frame,
            text="Test your knowledge with interactive quizzes!\nUse hand gestures (point left/right) to answer questions.",
            font=('Arial', 10),
            bg=self.current_theme['bg_frame'],
            fg='white',
            justify=tk.LEFT
        )
        self.quiz_desc.pack(pady=5)
        
        self.quiz_btn = tk.Button(
            self.quiz_frame,
            text="🎯 Start Quiz Mode",
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=10,
            command=self.start_quiz_mode,
            cursor='hand2'
        )
        self.quiz_btn.pack(pady=10)
        
        # Status frame
        self.status_frame = tk.Frame(self.root, bg=self.current_theme['bg_header'], relief=tk.SUNKEN, bd=2)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            font=('Arial', 10),
            bg=self.current_theme['bg_header'],
            fg='white'
        )
        self.status_label.pack(pady=5)
    
    def apply_theme(self, gender):
        """
        Apply gender-based theme to the GUI
        Args:
            gender: 'boy' or 'girl'
        """
        if gender.lower() == 'girl':
            self.current_theme = self.themes['girl']
        else:
            self.current_theme = self.themes['boy']
        
        # Update all UI elements with new theme colors
        self.root.configure(bg=self.current_theme['bg_main'])
        self.header_frame.configure(bg=self.current_theme['bg_header'])
        self.title_label.configure(
            text=self.current_theme['title'],
            bg=self.current_theme['bg_header'],
            fg='white'
        )
        self.user_frame.configure(bg=self.current_theme['bg_user'])
        self.content_frame.configure(bg=self.current_theme['bg_main'])
        
        # Update user label text color based on theme
        if hasattr(self, 'current_user') and self.current_user:
            gender_emoji = '👧' if gender.lower() == 'girl' else '👦'
            self.user_label.configure(
                bg=self.current_theme['bg_user'],
                fg='#2ecc71'  # Green for logged in status
            )
        else:
            self.user_label.configure(
                bg=self.current_theme['bg_user'],
                fg='#7f8c8d'  # Gray for not logged in
            )
        
        # Update frames
        self.auth_frame.configure(
            bg=self.current_theme['bg_frame'],
            fg='white'
        )
        self.btn_frame_auth.configure(bg=self.current_theme['bg_frame'])
        self.learning_frame.configure(
            bg=self.current_theme['bg_frame'],
            fg='white'
        )
        self.learning_desc.configure(
            bg=self.current_theme['bg_frame'],
            fg='white'
        )
        self.quiz_frame.configure(
            bg=self.current_theme['bg_frame'],
            fg='white'
        )
        self.quiz_desc.configure(
            bg=self.current_theme['bg_frame'],
            fg='white'
        )
        
        # Update buttons
        self.login_btn.configure(bg=self.current_theme['bg_button'])
        self.signup_btn.configure(bg=self.current_theme['success'])
        
        # Update status frame
        self.status_frame.configure(bg=self.current_theme['bg_header'])
        self.status_label.configure(
            bg=self.current_theme['bg_header'],
            fg='white'
        )
        
        # Force GUI update
        self.root.update_idletasks()
    
    def check_csharp_app(self):
        """Check if C# application exists"""
        csharp_path = "TUIO11_NET-master/TUIO11_NET-master update/bin/Debug/TuioDemo.exe"
        if not os.path.exists(csharp_path):
            self.status_label.config(
                text="Warning: C# quiz application not found. Learning and Quiz modes may not work.",
                fg='#f39c12'
            )
    
    def update_status(self, message, color=None):
        """Update status label"""
        if color is None:
            color = self.current_theme.get('accent', '#3498db')
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def face_login(self):
        """Handle face login"""
        if not FACE_AUTH_AVAILABLE:
            messagebox.showerror(
                "Error",
                "Face authentication is not available!\n\n"
                "Please install required packages:\n"
                "pip install face-recognition dlib"
            )
            return
        
        def login_thread():
            try:
                self.update_status("Starting face recognition...", '#3498db')
                auth = FaceAuthManager(camera_index=0)
                user_info = auth.login_child()
                
                if user_info:
                    user_name = user_info.get('name', user_info) if isinstance(user_info, dict) else user_info
                    user_gender = user_info.get('gender', 'boy') if isinstance(user_info, dict) else 'boy'
                    
                    self.current_user = user_name
                    self.current_user_gender = user_gender
                    
                    # Apply theme based on gender
                    self.root.after(0, lambda: self.apply_theme(user_gender))
                    
                    # Update user label
                    gender_emoji = '👧' if user_gender.lower() == 'girl' else '👦'
                    self.root.after(0, lambda: self.user_label.config(
                        text=f"{gender_emoji} Logged in as: {user_name}",
                        fg='#2ecc71'
                    ))
                    
                    # Update status
                    welcome_msg = f"Welcome {user_name}! {'🌸' if user_gender.lower() == 'girl' else '🎮'}"
                    self.root.after(0, lambda: self.update_status(
                        welcome_msg,
                        self.current_theme['accent']
                    ))
                    
                    # Send login message to C# app
                    self.send_login_message(user_name)
                else:
                    self.root.after(0, lambda: self.update_status(
                        "Login failed or cancelled",
                        '#e74c3c'
                    ))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(
                    f"Login error: {str(e)}",
                    '#e74c3c'
                ))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Login failed:\n{str(e)}"
                ))
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def face_signup(self):
        """Handle face signup"""
        if not FACE_AUTH_AVAILABLE:
            messagebox.showerror(
                "Error",
                "Face authentication is not available!\n\n"
                "Please install required packages:\n"
                "pip install face-recognition dlib"
            )
            return
        
        # Ask for child's name
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
        
        boy_btn = tk.Button(
            btn_frame,
            text="👦 Boy",
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='white',
            padx=30,
            pady=15,
            command=lambda: select_gender('boy'),
            cursor='hand2'
        )
        boy_btn.pack(side=tk.LEFT, padx=10)
        
        girl_btn = tk.Button(
            btn_frame,
            text="👧 Girl",
            font=('Arial', 14, 'bold'),
            bg='#ff69b4',
            fg='white',
            padx=30,
            pady=15,
            command=lambda: select_gender('girl'),
            cursor='hand2'
        )
        girl_btn.pack(side=tk.LEFT, padx=10)
        
        # Center the window
        gender_window.update_idletasks()
        x = (gender_window.winfo_screenwidth() // 2) - (gender_window.winfo_width() // 2)
        y = (gender_window.winfo_screenheight() // 2) - (gender_window.winfo_height() // 2)
        gender_window.geometry(f"+{x}+{y}")
        
        # Wait for user selection (window will be destroyed when button is clicked)
        gender_window.wait_window()
        
        gender = selected_gender['value']
        
        def signup_thread():
            try:
                self.update_status(f"Registering {name} ({gender})...", '#3498db')
                auth = FaceAuthManager(camera_index=0)
                success = auth.register_child(name, gender)
                
                if success:
                    gender_emoji = '👧' if gender.lower() == 'girl' else '👦'
                    self.root.after(0, lambda: self.update_status(
                        f"Registration successful for {name} {gender_emoji}!",
                        '#2ecc71'
                    ))
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success",
                        f"{name} ({gender.capitalize()}) has been registered successfully!"
                    ))
                else:
                    self.root.after(0, lambda: self.update_status(
                        "Registration failed or cancelled",
                        '#e74c3c'
                    ))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(
                    f"Registration error: {str(e)}",
                    '#e74c3c'
                ))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Registration failed:\n{str(e)}"
                ))
        
        threading.Thread(target=signup_thread, daemon=True).start()
    
    def logout(self):
        """Handle logout"""
        if self.current_user:
            self.current_user = None
            self.current_user_gender = None
            
            # Reset to default theme
            self.apply_theme('boy')
            
            self.user_label.config(text="Not logged in", fg='#7f8c8d')
            self.update_status("Logged out successfully", '#3498db')
        else:
            messagebox.showinfo("Info", "You are not logged in.")
    
    def start_learning_mode(self):
        """Start learning mode (C# application)"""
        csharp_path = "TUIO11_NET-master/TUIO11_NET-master update/bin/Debug/TuioDemo.exe"
        
        if not os.path.exists(csharp_path):
            messagebox.showerror(
                "Error",
                "C# learning application not found!\n\n"
                "Please build the C# project first or check the path."
            )
            return
        
        try:
            # Change to the directory containing the executable
            exe_dir = os.path.dirname(csharp_path)
            self.learning_process = subprocess.Popen(
                [csharp_path],
                cwd=exe_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            self.update_status("Learning mode started! Place markers 0-8 on the table.", '#2ecc71')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start learning mode: {str(e)}")
            self.update_status("Failed to start learning mode", '#e74c3c')
    
    def start_quiz_mode(self):
        """Start quiz mode (launches quiz_app.py from quiz side folder)"""
        quiz_launcher = "start_quiz.py"
        
        if not os.path.exists(quiz_launcher):
            messagebox.showerror(
                "Error",
                f"Quiz launcher script not found: {quiz_launcher}"
            )
            return
        
        try:
            # Launch quiz using the launcher script
            self.quiz_process = subprocess.Popen(
                [sys.executable, quiz_launcher],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            self.update_status(
                "Quiz mode started! Quiz window should appear shortly.",
                '#2ecc71'
            )
            messagebox.showinfo(
                "Quiz Mode Started",
                "Quiz application is starting!\n\n"
                "Instructions:\n"
                "- Use hand gestures (swipe left/right) for gesture questions\n"
                "- Use laser pointer to select answers for laser questions\n"
                "- Press 'q' to quit the quiz"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start quiz mode: {str(e)}")
            self.update_status("Failed to start quiz mode", '#e74c3c')
    
    def open_circular_menu(self):
        """Open circular menu window (controlled by TUIO markers)"""
        if not CIRCULAR_MENU_AVAILABLE:
            messagebox.showerror(
                "Error",
                "Circular menu module not available!\n\n"
                "Make sure circular_menu.py is in the project directory."
            )
            return
        
        # Close existing menu window if open
        if self.circular_menu_window is not None:
            try:
                self.circular_menu_window.destroy()
            except:
                pass
        
        # Create new menu window
        self.circular_menu_window = tk.Toplevel(self.root)
        self.circular_menu_window.title("Circular Menu - TUIO Controlled")
        self.circular_menu_window.geometry("800x850")
        self.circular_menu_window.configure(bg='#1a1a2e')
        
        # Add status label
        status_label = tk.Label(
            self.circular_menu_window,
            text="Place a TUIO marker on the menu to select an option\nHold marker in a sector for 1 second to confirm",
            font=('Arial', 12),
            bg='#1a1a2e',
            fg='white'
        )
        status_label.pack(pady=10)
        
        # Create callbacks that use existing methods
        callbacks = {
            'login': self.face_login,
            'signup': self.face_signup,
            'learning': self.start_learning_mode,
            'quiz': self.start_quiz_mode,
            'logout': self.logout
        }
        
        # Create circular menu
        self.circular_menu = create_main_menu(self.circular_menu_window, callbacks)
        
        # Handle window closing
        def on_menu_close():
            if self.circular_menu:
                try:
                    self.circular_menu.cleanup()
                except:
                    pass
            self.circular_menu_window = None
            self.circular_menu = None
        
        self.circular_menu_window.protocol("WM_DELETE_WINDOW", on_menu_close)
        
        self.update_status("Circular menu opened! Use TUIO markers to navigate.", '#9b59b6')
    
    def setup_login_socket_server(self):
        """Setup socket server to receive login updates from external scripts"""
        def handle_login_update():
            """Handle login updates from external scripts in a separate thread"""
            import socket as sock
            server_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
            server_socket.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
            server_socket.bind(('localhost', self.login_socket_port))
            server_socket.listen(5)
            server_socket.settimeout(1.0)  # Timeout to allow checking if still running
            
            while True:
                try:
                    client_socket, addr = server_socket.accept()
                    data = client_socket.recv(1024).decode('utf-8')
                    client_socket.close()
                    
                    if data:
                        try:
                            login_data = json.loads(data)
                            # Update GUI from external login
                            self.root.after(0, lambda: self.handle_external_login(login_data))
                        except json.JSONDecodeError:
                            pass
                except sock.timeout:
                    continue
                except Exception as e:
                    if self.root.winfo_exists():
                        continue
                    else:
                        break
            
            server_socket.close()
        
        # Start socket server in background thread
        threading.Thread(target=handle_login_update, daemon=True).start()
    
    def handle_external_login(self, login_data):
        """Handle login update from external script (like face_login.py)"""
        try:
            user_name = login_data.get('name', '')
            user_gender = login_data.get('gender', 'boy')
            
            if not user_name:
                return
            
            # Update current user
            self.current_user = user_name
            self.current_user_gender = user_gender
            
            # Apply theme based on gender
            self.apply_theme(user_gender)
            
            # Update user label
            gender_emoji = '👧' if user_gender.lower() == 'girl' else '👦'
            self.user_label.config(
                text=f"{gender_emoji} Logged in as: {user_name}",
                fg='#2ecc71'
            )
            
            # Update status
            welcome_msg = f"Welcome {user_name}! {'🌸' if user_gender.lower() == 'girl' else '🎮'}"
            self.update_status(
                welcome_msg,
                self.current_theme['accent']
            )
            
            # Send login message to C# app
            self.send_login_message(user_name)
            
            print(f"✅ GUI updated: {user_name} ({user_gender}) logged in via external script")
        except Exception as e:
            print(f"Error handling external login: {e}")
    
    def send_login_message(self, username):
        """Send login message to C# app via socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.socket_host, self.socket_port))
            
            message = {
                'type': 'login',
                'user': username,
                'timestamp': time.time()
            }
            data = json.dumps(message) + '\n'
            sock.sendall(data.encode('utf-8'))
            sock.close()
            print(f"Sent login message for: {username}")
        except Exception as e:
            print(f"Could not send login message (C# app may not be running): {e}")
    
    def on_closing(self):
        """Handle window closing"""
        # Stop any running processes
        if self.quiz_process:
            try:
                self.quiz_process.terminate()
            except:
                pass
        
        if self.hand_gesture_process:
            try:
                self.hand_gesture_process.terminate()
            except:
                pass
        
        if self.learning_process:
            try:
                self.learning_process.terminate()
            except:
                pass
        
        self.root.destroy()


def main():
    """Main entry point"""
    import sys
    
    root = tk.Tk()
    app = MainApplication(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # If command line argument is 'circular-menu', open it immediately
    if len(sys.argv) > 1 and sys.argv[1] == 'circular-menu':
        root.after(500, app.open_circular_menu)  # Small delay to ensure window is ready
    
    root.mainloop()


if __name__ == "__main__":
    main()

