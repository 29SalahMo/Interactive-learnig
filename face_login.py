from face_auth import FaceAuthManager
import socket
import json


def send_login_to_gui(name, gender):
    """Send login information to main GUI via socket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('localhost', 8889))  # Port for GUI login updates
        
        message = {
            'name': name,
            'gender': gender,
            'timestamp': __import__('time').time()
        }
        data = json.dumps(message)
        sock.sendall(data.encode('utf-8'))
        sock.close()
        print(f"[INFO] Sent login update to main GUI")
    except Exception as e:
        # GUI might not be running, that's okay
        print(f"[INFO] Main GUI not running or not listening: {e}")


def main() -> None:
    """
    Login a registered child using the webcam.
    Run from the project root:
        python face_login.py

    This will:
    1. Perform face recognition login
    2. Send login message to C# app on port 8888 (if running)
    3. Send login update to main GUI on port 8889 (if running)
    """
    auth = FaceAuthManager(camera_index=0)
    child_info = auth.login_child()

    if child_info:
        # Handle both dict and string return types (backward compatibility)
        if isinstance(child_info, dict):
            name = child_info.get('name', 'Unknown')
            gender = child_info.get('gender', 'boy')
            print(f"[OK] Login successful for: {name} ({gender})")
            
            # Send login update to main GUI if it's running
            send_login_to_gui(name, gender)
        else:
            # Fallback for old format
            name = child_info
            print(f"[OK] Login successful for: {name}")
            # Try to send update (gender will default to 'boy')
            send_login_to_gui(name, 'boy')
    else:
        print("[ERROR] Login failed or cancelled.")


if __name__ == "__main__":
    main()


