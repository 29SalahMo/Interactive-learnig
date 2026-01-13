"""
Test script to run quiz directly and see errors
"""
import os
import sys

# Change to quiz side directory
quiz_dir = os.path.join(os.path.dirname(__file__), "quiz side")
os.chdir(quiz_dir)
sys.path.insert(0, quiz_dir)

print(f"Working directory: {os.getcwd()}")
print(f"Quiz directory: {quiz_dir}")
print("=" * 50)

try:
    print("Testing imports...")
    import cv2
    print("[OK] cv2")
    import numpy as np
    print("[OK] numpy")
    import mediapipe as mp
    print("[OK] mediapipe")
    import pygame
    print("[OK] pygame")
    
    print("\nTesting quiz_app imports...")
    from questions_bank import hand_gesture_questions, laser_matching_type_A
    print("[OK] questions_bank")
    
    print("\nTesting quiz_app...")
    import quiz_app
    print("[OK] quiz_app imported")
    
    print("\nStarting quiz...")
    quiz_app.main()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")

