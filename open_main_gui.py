"""
Main GUI Launcher
Opens the main GUI application (main_gui.py)
Can be called by marker 15 from C# app
"""
import subprocess
import sys
import os

def main():
    """Launch main GUI"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    main_gui_script = os.path.join(project_root, "main_gui.py")
    
    if not os.path.exists(main_gui_script):
        print(f"ERROR: main_gui.py not found!")
        return
    
    try:
        # Launch main_gui.py
        subprocess.Popen(
            [sys.executable, main_gui_script],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        print("Main GUI launched!")
    except Exception as e:
        print(f"ERROR: Failed to launch main GUI: {e}")

if __name__ == "__main__":
    main()
