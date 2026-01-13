# ===============================================
#   GESTURE TRAINING + RECOGNITION SYSTEM
#   USING MEDIAPIPE + DOLLARPY
# ===============================================

import cv2
import mediapipe as mp
import numpy as np
import os
import time
from dollarpy import Recognizer, Template, Point

# ================================
#   GLOBALS
# ================================
templates = []   # DollarPy gesture templates

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


# =====================================================================================
#                           1) EXTRACT POINTS FROM VIDEO (DollarPy training)
# =====================================================================================
def getPoints(videoURL, label, timeout=10, show=False):
    """
    Extracts DollarPy points from video or webcam.
    Used for gesture template creation.
    show=False disables video display
    """
    cap = cv2.VideoCapture(videoURL)
    start_time = time.time()

    left_hand = [[] for _ in range(21)]
    right_hand = [[] for _ in range(21)]

    print(f"[TRAIN] Starting capture for '{label}'...")

    with mp_hands.Hands(min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if time.time() - start_time > timeout:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for h, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    is_left = results.multi_handedness[h].classification[0].label == "Left"

                    for i, lm in enumerate(hand_landmarks.landmark):
                        if is_left:
                            left_hand[i].append(Point(lm.x, lm.y, i + 1))
                        else:
                            right_hand[i].append(Point(lm.x, lm.y, i + 22))

                    if show:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if show:
                cv2.imshow(label, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cap.release()
    if show:
        cv2.destroyAllWindows()

    print(f"[TRAIN] Finished '{label}'.")

    points = [p for sub in (left_hand + right_hand) for p in sub]
    return points


# =====================================================================================
#                           2) TRAINING ALL GESTURES
# =====================================================================================
def train_gestures():
    """
    Reads training videos,
    extracts gesture points,
    creates DollarPy templates.
    """

    TRAINING = {
        "RightHandROption": r"e:\New folder\hci\project\videos\rRoption.mp4",
        "RightHandLOption": r"e:\New folder\hci\project\videos\rLoption.mp4",
        "LeftHandROption":  r"e:\New folder\hci\project\videos\Lroption.mp4",
        "LeftHandLOption":  r"e:\New folder\hci\project\videos\Lloption.mp4",
    }

    global templates
    templates = []

    for label, video in TRAINING.items():
        if not os.path.exists(video):
            print(f"[ERR] File not found: {video}")
            continue

        pts = getPoints(video, label, show=False)  # <-- عرض الفيديو مطفأ
        tmpl = Template(label, pts)
        templates.append(tmpl)
        print(f"[OK] Template added: {label} ({len(pts)} points)")

    print(f"\n[TRAIN] Total templates trained: {len(templates)}")
    return templates


# =====================================================================================
#                           3) REAL-TIME RECOGNITION (webcam)
# =====================================================================================
def recognize_live(timeout=15):
    """
    Capture live hand gesture and classify using trained templates.
    """
    if len(templates) == 0:
        print("[ERROR] No templates! Run train_gestures() first.")
        return

    recognizer = Recognizer(templates)
    
    print("\n[START] Capture your gesture...")
    pts = getPoints(0, "TEST-GESTURE", timeout=timeout, show=False)  # <-- عرض مطفأ

    if len(pts) == 0:
        print("[ERR] No points detected. Try again.")
        return

    print("[INFO] Running Recognition...")
    start = time.time()
    result = recognizer.recognize(pts)
    end = time.time()

    print("\n==================== RESULT ====================")
    if result:
        print(f"Recognized: {result[0]}")
    else:
        print("No matching gesture!")
    print(f"Time: {round(end - start, 2)} seconds")
    print("================================================")


# =====================================================================================
#                           MAIN ENTRY
# =====================================================================================
if __name__ == "__main__":

    print("\n==================== TRAINING ====================")
    train_gestures()

    print("\n==================== LIVE TEST ====================")
    recognize_live(timeout=12)
