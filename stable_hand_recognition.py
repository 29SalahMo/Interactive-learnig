import mediapipe as mp
import cv2
from dollarpy import Recognizer, Template, Point
import time
import os
import sys
import socket
import json
import threading

class StableHandGestureRecognizer:
    def __init__(self, camera_index=1):
        """
        Initialize hand gesture recognizer
        Args:
            camera_index: Which camera to use (0, 1, 2, etc.)
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.templates = []
        self.recognizer = None
        self.gesture_file = "current_gesture.txt"
        self.last_gesture = ""
        self.running = True
        self.camera_index = camera_index
        
        # Gesture confirmation timing
        self.current_gesture = None
        self.gesture_start_time = None
        self.confirmation_duration = 5.0  # 5 seconds to confirm
        self.confirmed_gesture = None
        
        # Socket communication
        self.socket_client = None
        self.socket_host = 'localhost'
        self.socket_port = 8888
        self.connect_to_socket()
        
        print("Hand Gesture Recognition Starting...")
        print(f"Using camera index: {camera_index}")
        print("Socket communication enabled")
    
    def connect_to_socket(self):
        """Connect to C# socket server"""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_client.connect((self.socket_host, self.socket_port))
                print(f"Connected to C# via socket on {self.socket_host}:{self.socket_port}")
                return True
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Socket connection attempt {retry_count}/{max_retries} failed, retrying...")
                    time.sleep(2)
                else:
                    print(f"Socket connection failed after {max_retries} attempts: {e}")
                    print("Continuing without socket communication")
                    self.socket_client = None
                    return False
    
    def send_via_socket(self, data):
        """Send data via socket to C#"""
        if self.socket_client:
            try:
                message = json.dumps(data) + '\n'
                self.socket_client.sendall(message.encode('utf-8'))
                return True
            except Exception as e:
                print(f"Socket send error: {e}")
                self.socket_client = None
                return False
        return False
        
    def load_templates(self):
        """Load pre-trained gesture templates"""
        print("Loading gesture templates...")
        
        # Create sample templates for demonstration
        # Right Hand R Option (Pointing Right)
        right_r_points = [
            Point(0.5, 0.5, 1), Point(0.6, 0.5, 1), Point(0.7, 0.5, 1),
            Point(0.8, 0.5, 1), Point(0.9, 0.5, 1)
        ]
        self.templates.append(Template("RightHandROption", right_r_points))
        
        # Right Hand L Option (Pointing Left)
        right_l_points = [
            Point(0.5, 0.5, 1), Point(0.4, 0.5, 1), Point(0.3, 0.5, 1),
            Point(0.2, 0.5, 1), Point(0.1, 0.5, 1)
        ]
        self.templates.append(Template("RightHandLOption", right_l_points))
        
        # Left Hand R Option (Pointing Right with Left Hand)
        left_r_points = [
            Point(0.5, 0.5, 2), Point(0.6, 0.5, 2), Point(0.7, 0.5, 2),
            Point(0.8, 0.5, 2), Point(0.9, 0.5, 2)
        ]
        self.templates.append(Template("LeftHandROption", left_r_points))
        
        # Left Hand L Option (Pointing Left with Left Hand)
        left_l_points = [
            Point(0.5, 0.5, 2), Point(0.4, 0.5, 2), Point(0.3, 0.5, 2),
            Point(0.2, 0.5, 2), Point(0.1, 0.5, 2)
        ]
        self.templates.append(Template("LeftHandLOption", left_l_points))
        
        print(f"Loaded {len(self.templates)} gesture templates")
        
    def write_gesture_to_file(self, gesture):
        """Write recognized gesture to file AND socket for C# GUI to read"""
        try:
            # Write to file (legacy support)
            with open(self.gesture_file, 'w') as f:
                f.write(gesture)
            
            # ALSO send via socket for real-time communication
            if gesture:
                gesture_type = "right" if "ROption" in gesture else "left" if "LOption" in gesture else gesture
                socket_data = {
                    'type': 'gesture',
                    'gesture': gesture_type.lower(),
                    'timestamp': time.time()
                }
                self.send_via_socket(socket_data)
                print(f"CONFIRMED - Sent via socket: {socket_data}")
        except Exception as e:
            print(f"Error writing gesture: {e}")
    
    def run_stable_recognition(self):
        """Run stable gesture recognition with persistent camera window"""
        print("Starting stable hand gesture recognition...")
        print("Camera window will stay open - Press 'q' to quit")
        print("=" * 50)
        
        # Initialize camera
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"ERROR: Could not open camera {self.camera_index}")
            print(f"Available cameras: Checking...")
            # Try to find another camera
            for i in range(3):
                if i != self.camera_index:
                    test_cap = cv2.VideoCapture(i)
                    if test_cap.isOpened():
                        print(f"Camera {i} is available")
                        test_cap.release()
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize MediaPipe hands
        with self.mp_hands.Hands(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7,
            max_num_hands=2
        ) as hands:
            
            print("Camera window opened - Show hand gestures to test recognition")
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    print("ERROR: Could not read from camera")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process frame
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Draw landmarks and connections
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(
                            image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )
                
                # Add instruction text
                cv2.putText(image, "Show hand gestures - Press 'q' to quit", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show current gesture confirmation status
                if self.current_gesture and self.gesture_start_time:
                    elapsed = time.time() - self.gesture_start_time
                    if elapsed < self.confirmation_duration:
                        progress = elapsed / self.confirmation_duration
                        countdown = int(self.confirmation_duration - elapsed) + 1
                        
                        if "LOption" in self.current_gesture:
                            gesture_text = "LEFT ANSWER (A)"
                            color = (0, 255, 0)  # Green
                        elif "ROption" in self.current_gesture:
                            gesture_text = "RIGHT ANSWER (B)"
                            color = (0, 165, 255)  # Orange
                        else:
                            gesture_text = self.current_gesture
                            color = (255, 0, 0)
                        
                        # Show countdown
                        cv2.putText(image, f"Holding: {gesture_text}", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        cv2.putText(image, f"Confirm in: {countdown} seconds", 
                                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        # Draw progress bar
                        bar_width = int(400 * progress)
                        cv2.rectangle(image, (10, 100), (10 + bar_width, 115), color, -1)
                        cv2.rectangle(image, (10, 100), (410, 115), (255, 255, 255), 2)
                elif self.confirmed_gesture:
                    cv2.putText(image, "ANSWER SENT!", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3)
                
                # Show instruction text
                cv2.putText(image, "Hold finger LEFT or RIGHT for 5 seconds", 
                           (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display the frame
                cv2.imshow("Hand Gesture Recognition - Press 'q' to quit", image)
                
                # Check for quit command
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quit command received")
                    break
                
                # Process gestures every 30 frames (about 1 second at 30fps)
                if hasattr(self, 'frame_count'):
                    self.frame_count += 1
                else:
                    self.frame_count = 0
                
                if self.frame_count % 30 == 0:
                    self.process_current_gesture(results)
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Camera closed - Hand gesture recognition stopped")
    
    def process_current_gesture(self, results):
        """Process current hand landmarks for simple left/right detection with 5-second confirmation"""
        try:
            current_time = time.time()
            
            if not results.multi_hand_landmarks:
                # No hand detected - reset everything
                if self.gesture_start_time:
                    self.current_gesture = None
                    self.gesture_start_time = None
                    self.confirmed_gesture = None
                if self.last_gesture:
                    self.write_gesture_to_file("")
                    self.last_gesture = ""
                return
            
            # Get the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Get wrist position (landmark 0) - this is the base of the hand
            wrist = hand_landmarks.landmark[0]
            
            # Get index finger tip (landmark 8)
            index_tip = hand_landmarks.landmark[8]
            
            # Simple detection: check if index finger is extended and pointing direction
            middle_tip = hand_landmarks.landmark[12]
            
            # Check if index finger is extended (index tip Y is above middle tip Y)
            index_extended = index_tip.y < middle_tip.y
            
            if index_extended:
                # Determine left or right based on index finger position relative to wrist
                if index_tip.x < wrist.x - 0.05:  # Pointing left (adjusted threshold)
                    detected_gesture = "LeftHandLOption"
                elif index_tip.x > wrist.x + 0.05:  # Pointing right (adjusted threshold)
                    detected_gesture = "RightHandROption"
                else:
                    # Not pointing clearly, don't set a gesture
                    detected_gesture = None
                
                if detected_gesture:
                    # Check if this is a new gesture or continuation of current
                    if detected_gesture == self.current_gesture:
                        # Same gesture - check if confirmation time has passed
                        if self.gesture_start_time and (current_time - self.gesture_start_time) >= self.confirmation_duration:
                            # Confirm and send if not already sent
                            if not self.confirmed_gesture or self.confirmed_gesture != detected_gesture:
                                print(f"Gesture CONFIRMED after 5 seconds: {detected_gesture}")
                                self.write_gesture_to_file(detected_gesture)
                                self.last_gesture = detected_gesture
                                self.confirmed_gesture = detected_gesture
                                # Reset after sending
                                self.current_gesture = None
                                self.gesture_start_time = None
                                # Clear confirmed gesture after a brief delay
                                time.sleep(0.5)
                                self.confirmed_gesture = None
                    else:
                        # New gesture detected - start timing
                        self.current_gesture = detected_gesture
                        self.gesture_start_time = current_time
                        self.confirmed_gesture = None
                        print(f"New gesture detected (hold for 5s): {detected_gesture}")
                else:
                    # Gesture unclear - reset
                    self.current_gesture = None
                    self.gesture_start_time = None
                    self.confirmed_gesture = None
            else:
                # Finger not extended - reset
                self.current_gesture = None
                self.gesture_start_time = None
                self.confirmed_gesture = None
                    
        except Exception as e:
            print(f"Error processing gesture: {e}")
    
    def recognize_gesture(self, points):
        """Recognize gesture from hand landmarks"""
        if not self.templates or not points:
            return None
            
        try:
            self.recognizer = Recognizer(self.templates)
            result = self.recognizer.recognize(points)
            return result
        except Exception as e:
            return None

def main():
    """Main function"""
    print("Stable Hand Gesture Recognition for TuioKidsQuiz")
    print("=" * 50)
    
    # Allow camera selection via command line argument
    camera_index = 1  # Default: camera 1 (second camera for hand gestures)
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except:
            print("Usage: python stable_hand_recognition.py [camera_index]")
            print("Example: python stable_hand_recognition.py 1")
            print("Available cameras: 0, 1, 2, etc.")
            print("\nRun 'python check_cameras.py' to see available cameras")
            sys.exit(1)
    
    print(f"Using camera index: {camera_index}")
    print("If this doesn't work, run: python check_cameras.py")
    print("=" * 50)
    
    try:
        recognizer = StableHandGestureRecognizer(camera_index=camera_index)
        
        # Load templates
        recognizer.load_templates()
        
        # Run stable recognition
        recognizer.run_stable_recognition()
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
    
    finally:
        # Cleanup
        if os.path.exists("current_gesture.txt"):
            os.remove("current_gesture.txt")
        print("Cleanup completed")

if __name__ == "__main__":
    main()
