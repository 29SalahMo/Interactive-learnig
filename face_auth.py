"""
Face Authentication Manager for child login/signup
Uses face_recognition library for face detection and recognition
"""
import cv2
import os
import pickle
import socket
import json
import time

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition library not found. Install with: pip install face-recognition")

try:
    from database import ChildDatabase
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Warning: database module not found. Install database.py in the same directory.")


class FaceAuthManager:
    """Manages face registration and login for children"""
    
    def __init__(self, camera_index=0):
        """
        Initialize face authentication manager
        Args:
            camera_index: Camera device index (0, 1, 2, etc.)
        """
        self.camera_index = camera_index
        
        # Initialize database if available
        if DATABASE_AVAILABLE:
            self.db = ChildDatabase()
            self.use_database = True
        else:
            # Fallback to pickle file system
            self.faces_dir = "faces"
            self.encodings_file = os.path.join(self.faces_dir, "encodings.pkl")
            os.makedirs(self.faces_dir, exist_ok=True)
            self.known_encodings = {}
            self.load_encodings()
            self.use_database = False
        
        # Socket for communication with C# app
        self.socket_client = None
        self.socket_host = 'localhost'
        self.socket_port = 8888
        
    def load_encodings(self):
        """Load saved face encodings from file (fallback method)"""
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    self.known_encodings = pickle.load(f)
                print(f"Loaded {len(self.known_encodings)} registered faces")
            except Exception as e:
                print(f"Error loading encodings: {e}")
                self.known_encodings = {}
        else:
            self.known_encodings = {}
    
    def get_all_encodings(self):
        """Get all face encodings (from database or pickle file)"""
        if self.use_database:
            return self.db.get_all_face_encodings()
        else:
            return self.known_encodings
    
    def connect_to_socket(self):
        """Connect to C# socket server"""
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.connect((self.socket_host, self.socket_port))
            return True
        except Exception as e:
            print(f"Socket connection failed (C# app may not be running): {e}")
            self.socket_client = None
            return False
    
    def send_login_message(self, child_name):
        """Send login message to C# app via socket"""
        if not self.socket_client:
            if not self.connect_to_socket():
                return False
        
        try:
            message = {
                'type': 'login',
                'user': child_name,
                'timestamp': time.time()
            }
            data = json.dumps(message) + '\n'
            self.socket_client.sendall(data.encode('utf-8'))
            print(f"Sent login message for: {child_name}")
            return True
        except Exception as e:
            print(f"Error sending login message: {e}")
            self.socket_client = None
            return False
    
    def register_child(self, name, gender='boy'):
        """
        Register a new child by capturing and encoding their face
        Args:
            name: Child's name
            gender: Child's gender ('boy' or 'girl'), default is 'boy'
        Returns:
            True if registration successful, False otherwise
        """
        if not FACE_RECOGNITION_AVAILABLE:
            print("ERROR: face_recognition library not available")
            return False
        
        # Check if child already exists
        if self.use_database:
            existing = self.db.get_child_by_name(name)
            if existing:
                print(f"Child '{name}' is already registered!")
                response = input("Do you want to re-register? (y/n): ").strip().lower()
                if response != 'y':
                    return False
        else:
            if name in self.known_encodings:
                print(f"Child '{name}' is already registered!")
                response = input("Do you want to re-register? (y/n): ").strip().lower()
                if response != 'y':
                    return False
        
        print(f"\nRegistering {name}...")
        print("Please look at the camera. Press SPACE to capture, ESC to cancel.")
        
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"ERROR: Could not open camera {self.camera_index}")
            return False
        
        captured = False
        encoding = None
        
        while not captured:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Could not read from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(rgb_frame)
            
            # Draw rectangle around face
            if face_locations:
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Face detected - Press SPACE", 
                           (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "No face detected - Look at camera", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.putText(frame, f"Registering: {name}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "SPACE = Capture | ESC = Cancel", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("Face Registration", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Spacebar
                if face_locations:
                    # Encode the face
                    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    if encodings:
                        encoding = encodings[0]
                        captured = True
                    else:
                        print("Could not encode face. Try again.")
                else:
                    print("No face detected. Please look at the camera.")
            elif key == 27:  # ESC
                print("Registration cancelled.")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if encoding is not None:
            # Save to database or pickle file
            if self.use_database:
                success = self.db.add_child(name, gender, encoding)
                if success:
                    print(f"Successfully registered {name} ({gender})!")
                    return True
                else:
                    print("Failed to save to database.")
                    return False
            else:
                # Fallback to pickle file (no gender stored)
                self.known_encodings[name] = encoding
                try:
                    with open(self.encodings_file, 'wb') as f:
                        pickle.dump(self.known_encodings, f)
                    print(f"Successfully registered {name}!")
                    return True
                except Exception as e:
                    print(f"Failed to save encoding: {e}")
                    return False
        else:
            return False
    
    def login_child(self):
        """
        Login a registered child by recognizing their face
        Returns:
            Dictionary with 'name' and 'gender' if login successful, None otherwise
        """
        if not FACE_RECOGNITION_AVAILABLE:
            print("ERROR: face_recognition library not available")
            return None
        
        # Get all encodings
        known_encodings = self.get_all_encodings()
        
        if not known_encodings:
            print("No registered children found. Please register first.")
            return None
        
        print("\nLogging in...")
        print("Please look at the camera. Press ESC to cancel.")
        
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"ERROR: Could not open camera {self.camera_index}")
            return None
        
        recognized_name = None
        recognition_count = 0
        required_matches = 5  # Require 5 consecutive matches for confirmation
        
        while recognized_name is None:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Could not read from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            match_found = False
            match_name = None
            
            if face_encodings:
                # Compare with known faces
                for encoding in face_encodings:
                    for name, known_encoding in known_encodings.items():
                        matches = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.6)
                        if matches[0]:
                            match_found = True
                            match_name = name
                            break
                    if match_found:
                        break
            
            # Draw on frame
            if face_locations:
                top, right, bottom, left = face_locations[0]
                if match_found:
                    color = (0, 255, 0)  # Green for match
                    text = f"Recognized: {match_name} ({recognition_count + 1}/{required_matches})"
                    recognition_count += 1
                    if recognition_count >= required_matches:
                        recognized_name = match_name
                else:
                    color = (0, 0, 255)  # Red for no match
                    text = "Face not recognized"
                    recognition_count = 0
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, text, (left, top - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                cv2.putText(frame, "No face detected - Look at camera", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                recognition_count = 0
            
            cv2.putText(frame, "Face Login - Press ESC to cancel", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Face Login", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("Login cancelled.")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if recognized_name:
            # Update last login timestamp
            if self.use_database:
                self.db.update_last_login(recognized_name)
                child_info = self.db.get_child_by_name(recognized_name)
                if child_info:
                    # Send login message to C# app
                    self.send_login_message(recognized_name)
                    return {
                        'name': child_info['name'],
                        'gender': child_info['gender']
                    }
            else:
                # Fallback: return just name (gender unknown)
                self.send_login_message(recognized_name)
                return {
                    'name': recognized_name,
                    'gender': 'boy'  # Default for backward compatibility
                }
        
        return None

