"""
Quiz Launcher Script
Launches quiz_app.py from the quiz side folder
Called by marker 11 or can be run directly
"""
import subprocess
import sys
import os

def main():
    """Launch quiz application from quiz side folder"""
    print("=" * 50)
    print("Starting Quiz Application")
    print("=" * 50)
    
    # Get the project root directory (where this script is located)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Path to quiz_app.py in the quiz side folder
    quiz_script = os.path.join(project_root, "quiz side", "quiz_app.py")
    
    # Check if script exists
    if not os.path.exists(quiz_script):
        print(f"ERROR: Quiz script not found at {quiz_script}!")
        print(f"Current directory: {os.getcwd()}")
        input("Press Enter to exit...")
        return
    
    try:
        # Change to quiz side directory so relative paths (images/, sounds/) work correctly
        quiz_dir = os.path.join(project_root, "quiz side")
        
        print(f"Launching quiz from: {quiz_dir}")
        print(f"Script: {quiz_script}")
        print("=" * 50)
        
        # Check if required files exist
        questions_file = os.path.join(quiz_dir, "questions_bank.py")
        if not os.path.exists(questions_file):
            print(f"ERROR: questions_bank.py not found at {questions_file}")
            input("Press Enter to exit...")
            return
        
        # Launch quiz_app.py from the quiz side directory
        # Pass camera index 0 as default (quiz will auto-detect if unavailable)
        process = subprocess.Popen(
            [sys.executable, quiz_script, "0"],
            cwd=quiz_dir,  # Set working directory to quiz side folder
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        print("Quiz application started!")
        print("If the window closes immediately, check the console for error messages.")
        print("Instructions:")
        print("  - Use hand gestures (swipe left/right) to answer gesture questions")
        print("  - Use laser pointer to select answers for laser questions")
        print("  - Press 'q' to quit")
        print("\nNote: Make sure your camera is connected and accessible.")
        
    except Exception as e:
        print(f"ERROR: Failed to start quiz: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

