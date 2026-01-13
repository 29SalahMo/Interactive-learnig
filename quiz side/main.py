# main.py
import gesture_training_and_recognition as gesture_module
import quiz_app
import time

def main():
    print("\n==================== GESTURE TRAINING ====================")
    # Step 1: Train gestures (DollarPy templates)
    templates = gesture_module.train_gestures()
    print(f"[MAIN] Templates trained: {len(templates)}")

    # Optional: Test live recognition before starting quiz
    print("\n==================== LIVE GESTURE TEST ====================")
    gesture_module.recognize_live(timeout=8)

    # Step 2: Launch quiz app (laser + hand swipe)
    print("\n==================== STARTING QUIZ ====================")
    quiz_app.main()

if __name__ == "__main__":
    main()
