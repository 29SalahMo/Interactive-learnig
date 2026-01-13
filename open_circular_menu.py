"""
Circular Menu Launcher
Opens the circular menu interface from main_gui.py
Can be called by marker 12 from C# app
"""
import subprocess
import sys
import os

def main():
    """Launch circular menu via main GUI with argument"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    main_gui_script = os.path.join(project_root, "main_gui.py")
    
    if not os.path.exists(main_gui_script):
        print(f"ERROR: main_gui.py not found!")
        return
    
    try:
        # Launch main_gui.py with 'circular-menu' argument
        # This will automatically open the circular menu
        subprocess.Popen(
            [sys.executable, main_gui_script, "circular-menu"],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        print("Circular menu launched!")
    except Exception as e:
        print(f"ERROR: Failed to launch circular menu: {e}")

if __name__ == "__main__":
    main()



