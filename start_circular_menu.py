"""
Circular Menu Launcher Script
Launches the circular menu interface via main_gui.py
Called by marker 12 or can be run directly
"""
import subprocess
import sys
import os

def main():
    """Launch circular menu via main GUI"""
    print("=" * 50)
    print("Starting Circular Menu Interface")
    print("=" * 50)
    
    # Get the project root directory (where this script is located)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Check if main_gui.py exists
    main_gui_script = os.path.join(project_root, "main_gui.py")
    
    if not os.path.exists(main_gui_script):
        print(f"ERROR: main_gui.py not found at {main_gui_script}!")
        print(f"Current directory: {os.getcwd()}")
        input("Press Enter to exit...")
        return
    
    try:
        # Import and use main_gui to open circular menu
        # We'll need to modify main_gui to support command line argument
        print("Note: Circular menu can be opened via marker 12 or GUI button")
        print("Starting main GUI...")
        print("Use marker 12 or click 'Open Circular Menu' button")
        
        # For now, just start the main GUI
        # The user can then use marker or button to open circular menu
        subprocess.Popen(
            [sys.executable, main_gui_script],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        print("Main GUI started. Circular menu can be accessed via:")
        print("  - Marker 12 (if configured in C# app)")
        print("  - Click 'Open Circular Menu' button in GUI")
        
    except Exception as e:
        print(f"ERROR: Failed to start: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()



