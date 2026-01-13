# quiz_app.py
import cv2
import numpy as np
import mediapipe as mp
import time
import pygame
import math
from collections import deque
import os
import sys
from questions_bank import hand_gesture_questions, laser_matching_type_A

# ============================
# Configuration
# ============================
# Allow camera index to be specified via command line argument
CAM_INDEX = 0  # Default
if len(sys.argv) > 1:
    try:
        CAM_INDEX = int(sys.argv[1])
    except:
        print(f"Warning: Invalid camera index argument, using default: {CAM_INDEX}")
WINDOW_NAME = "Kids Quiz (Laser + Hand Gesture)"
FPS_CAP = 30

LOWER_HSV = np.array([0, 0, 200])
UPPER_HSV = np.array([180, 40, 255])

MAX_POINTS = 512
SMOOTHING_WINDOW = 4
MOVE_THRESHOLD = 6
CLEAR_AFTER_SECONDS = 2.5

HAND_MOVE_THRESHOLD = 30
GESTURE_TIME_WINDOW = 1.2

WIN_W = 1000
WIN_H = 600
IMG_BOX = (30, 30, 420, 420)
CHOICE_START_X = 500
CHOICE_START_Y = 80
CHOICE_W = 420
CHOICE_H = 90
CHOICE_GAP = 20

# Audio init
pygame.mixer.init()
def play_sound(path):
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    except Exception as e:
        print("Audio error:", e)

# ============================
# Helper functions
# ============================
def point_in_rect(pt, rect):
    if pt is None:
        return False
    x, y = pt
    rx, ry, rw, rh = rect
    return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)

def draw_button(frame, rect, text, color=(255,255,255), text_color=(0,0,0)):
    rx, ry, rw, rh = rect
    cv2.rectangle(frame, (rx, ry), (rx+rw, ry+rh), color, -1)
    cv2.rectangle(frame, (rx, ry), (rx+rw, ry+rh), (0,0,0), 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1.0
    thickness = 2
    text_size = cv2.getTextSize(text, font, scale, thickness)[0]
    tx = rx + (rw - text_size[0]) // 2
    ty = ry + (rh + text_size[1]) // 2
    cv2.putText(frame, text, (tx, ty), font, scale, text_color, thickness, cv2.LINE_AA)

def draw_image_into(frame, img_path, box):
    x,y,w,h = box
    if not img_path or not os.path.exists(img_path):
        base_names = ["apple","banana","cat","dog","elephant","orange","circle","triangle","rectangle"]
        found = False
        for name in base_names:
            for ext in [".jpg",".jpeg",".png"]:
                temp_path = f"images/{name}{ext}"
                if os.path.exists(temp_path):
                    img_path = temp_path
                    found = True
                    break
            if found:
                break
    try:
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(img_path)
        img = cv2.resize(img, (w,h))
        frame[y:y+h, x:x+w] = img
    except Exception as e:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (80,80,80), -1)
        cv2.putText(frame, "Image missing", (x+10, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

# ============================
# Laser tracking
# ============================
class LaserTracker:
    def __init__(self, cam_index=0):
        # Try to find an available camera
        self.cap = None
        cameras_to_try = [cam_index] + [i for i in range(3) if i != cam_index]
        working_idx = None
        
        for idx in cameras_to_try:
            test_cap = cv2.VideoCapture(idx)
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                if ret and frame is not None:
                    test_cap.release()
                    self.cap = cv2.VideoCapture(idx)
                    working_idx = idx
                    print(f"Using camera index: {idx}")
                    break
                else:
                    test_cap.release()
        
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError(f"Cannot open any camera. Tried indices: {cameras_to_try}")
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.cap.release()
            raise RuntimeError(f"Cannot read from camera index {working_idx}")
        self.canvas = np.zeros_like(frame)
        self.points = deque(maxlen=MAX_POINTS)
        self.coords_log = []
        self.last_move_time = None
        self.last_point = None

    def update(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None
        frame = cv2.flip(frame,1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)
        mask = cv2.GaussianBlur(mask, (7,7),0)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        current_point = None
        now = time.time()
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 80:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"]/M["m00"])
                    cy = int(M["m01"]/M["m00"])
                    current_point = (cx, cy)
                    x,y,w,h = cv2.boundingRect(largest)
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0),2)
                    cv2.circle(frame, current_point, 4, (0,255,0), -1)
        smoothed = None
        if current_point is not None:
            if len(self.points) >= SMOOTHING_WINDOW:
                recent = list(self.points)[-(SMOOTHING_WINDOW-1):] if SMOOTHING_WINDOW>1 else []
                recent.append(current_point)
                avg_x = int(sum(p[0] for p in recent)/len(recent))
                avg_y = int(sum(p[1] for p in recent)/len(recent))
                smoothed = (avg_x, avg_y)
            else:
                smoothed = current_point
            if self.last_point is None:
                self.last_move_time = now
            else:
                if math.hypot(smoothed[0]-self.last_point[0], smoothed[1]-self.last_point[1]) > MOVE_THRESHOLD:
                    self.last_move_time = now
            self.last_point = smoothed
            self.points.append(smoothed)
            self.coords_log.append(smoothed)
        else:
            if self.last_move_time is not None and (now - self.last_move_time) >= CLEAR_AFTER_SECONDS:
                self.points.clear()
                self.canvas = np.zeros_like(frame)
                self.last_point = None
                self.last_move_time = None
        for i in range(1,len(self.points)):
            if self.points[i-1] is None or self.points[i] is None:
                continue
            cv2.line(self.canvas, self.points[i-1], self.points[i], (0,255,0),2)
        output = cv2.addWeighted(frame,1.0,self.canvas,0.8,0)
        return output, smoothed, mask

    def release(self):
        self.cap.release()

# ============================
# Hand gesture detector
# ============================
class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1,
                                         min_detection_confidence=0.6,
                                         min_tracking_confidence=0.6)

    def update(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        hand_center = None
        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark[9]
            x = int(lm.x*frame.shape[1])
            y = int(lm.y*frame.shape[0])
            hand_center = (x,y)
            mp.solutions.drawing_utils.draw_landmarks(frame, results.multi_hand_landmarks[0], self.mp_hands.HAND_CONNECTIONS)
        return hand_center

    def detect_swipe(self, hand_centers):
        if len(hand_centers)<2:
            return None
        now = time.time()
        window = [p for p in hand_centers if now - p[2]<=GESTURE_TIME_WINDOW]
        if len(window)<2:
            return None
        dx = window[-1][0]-window[0][0]
        if dx>HAND_MOVE_THRESHOLD:
            return "right"
        elif dx<-HAND_MOVE_THRESHOLD:
            return "left"
        else:
            return None

# ============================
# Quiz Engine
# ============================
class QuizEngine:
    def __init__(self, questions_hand, questions_laser):
        self.hand_questions = questions_hand
        self.laser_questions = []

        for obj in questions_laser:
            for item, grp in obj["items"].items():
                img_path = ""
                for ext in [".jpg",".jpeg",".png"]:
                    temp_path = f"images/{item}{ext}"
                    if os.path.exists(temp_path):
                        img_path = temp_path
                        break
                self.laser_questions.append({
                    "image": img_path,
                    "choices": obj["groups"],
                    "correct_group": grp
                })

        self.sequence = []
        for hq in self.hand_questions:
            img_path = ""
            for name in [hq["left"].lower(), hq["right"].lower()]:
                for ext in [".jpg",".jpeg",".png"]:
                    temp = f"images/{name}{ext}"
                    if os.path.exists(temp):
                        img_path = temp
                        break
                if img_path:
                    break
            hq["image"] = img_path
            self.sequence.append(("gesture", hq))
        for lq in self.laser_questions:
            self.sequence.append(("laser", lq))
        self.index = 0
        self.score = 0

    def has_next(self):
        return self.index < len(self.sequence)

    def next(self):
        if not self.has_next():
            return None
        t,q = self.sequence[self.index]
        self.index +=1
        return t,q

    def check_answer(self, qtype, qdata, answer):
        correct = False
        if qtype=="gesture":
            if answer==qdata.get("answer"):
                correct = True
        else:
            if answer==qdata.get("correct_group"):
                correct = True
        if correct:
            self.score+=1
        return correct

# ============================
# Main App
# ============================
def main():
    try:
        print("Initializing camera...")
        print(f"Trying camera index: {CAM_INDEX}")
        laser = LaserTracker(cam_index=CAM_INDEX)
        print("Camera initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize camera: {e}")
        print(f"Make sure a camera is available (tried index {CAM_INDEX} and others)")
        print("Waiting 3 seconds before exit...")
        time.sleep(3)  # Wait instead of input() so it works when launched from C#
        return
    
    try:
        print("Initializing hand gesture detector...")
        hand = HandGestureDetector()
        print("Hand gesture detector initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize hand gesture detector: {e}")
        import traceback
        traceback.print_exc()
        print("Waiting 3 seconds before exit...")
        time.sleep(3)
        return
    
    try:
        print("Loading quiz questions...")
        quiz = QuizEngine(hand_gesture_questions, laser_matching_type_A)
        print(f"Quiz loaded: {quiz.index} questions")
    except Exception as e:
        print(f"ERROR: Failed to load quiz: {e}")
        import traceback
        traceback.print_exc()
        print("Waiting 3 seconds before exit...")
        time.sleep(3)
        return

    try:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, WIN_W, WIN_H)
        print("Quiz window created")
    except Exception as e:
        print(f"ERROR: Failed to create window: {e}")
        import traceback
        traceback.print_exc()
        print("Waiting 3 seconds before exit...")
        time.sleep(3)
        return

    hand_history = []

    current = quiz.next()
    wait_after_feedback = 1.4
    feedback_text = ""
    
    print("Starting quiz loop...")

    while current is not None:
        qtype,qdata = current
        answered = False
        selected_answer = None
        while not answered:
            frame_raw, laser_point, mask = laser.update()
            if frame_raw is None:
                break
            frame = cv2.resize(frame_raw, (WIN_W, WIN_H))

            if qtype=="gesture":
                draw_image_into(frame, qdata.get("image",""), IMG_BOX)

                left_rect = (IMG_BOX[0], IMG_BOX[1]+IMG_BOX[3]+10, 200, 80)
                right_rect = (IMG_BOX[0]+IMG_BOX[2]-200, IMG_BOX[1]+IMG_BOX[3]+10, 200, 80)
                draw_button(frame, left_rect, qdata["left"], color=(200,200,255))
                draw_button(frame, right_rect, qdata["right"], color=(200,200,255))
                cv2.putText(frame, qdata["question"], (IMG_BOX[0], IMG_BOX[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255),2)

                hand_center = hand.update(frame)
                if hand_center:
                    hand_history.append((hand_center[0], hand_center[1], time.time()))
                    # حافظ على نقاط اليد لمدة GESTURE_TIME_WINDOW فقط
                    now = time.time()
                    hand_history = [p for p in hand_history if now - p[2] <= GESTURE_TIME_WINDOW]
                    gesture = hand.detect_swipe(hand_history)
                    if gesture:
                        selected_answer = "right" if gesture=="right" else "left"
                        answered=True
            else:
                draw_image_into(frame, qdata.get("image",""), IMG_BOX)
                choices = qdata["choices"]
                answer_boxes = []
                for i, choice in enumerate(choices):
                    rx = CHOICE_START_X
                    ry = CHOICE_START_Y + i*(CHOICE_H+CHOICE_GAP)
                    rect = (rx, ry, CHOICE_W, CHOICE_H)
                    answer_boxes.append((choice, rect))
                    draw_button(frame, rect, choice, color=(220,220,220), text_color=(0,0,0))
                cv2.putText(frame, "Point the laser to the correct group", (CHOICE_START_X, CHOICE_START_Y-30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),2)
                if laser_point is not None:
                    cam_h, cam_w = frame_raw.shape[:2]
                    fx = int(laser_point[0]*WIN_W/cam_w)
                    fy = int(laser_point[1]*WIN_H/cam_h)
                    cv2.circle(frame, (fx, fy), 10, (0,255,0), -1)
                    for choice, rect in answer_boxes:
                        if point_in_rect((fx,fy), rect):
                            selected_answer = choice
                            answered = True
                            break

            if answered:
                correct_flag = quiz.check_answer(qtype,qdata,selected_answer)
                feedback_text = "Correct!" if correct_flag else "Wrong!"
                play_sound("sounds/correct.wav" if correct_flag else "sounds/wrong.wav")
                cv2.putText(frame, feedback_text, (WIN_W//2-60, WIN_H-60), cv2.FONT_HERSHEY_SIMPLEX,2.0,
                            (0,255,0) if correct_flag else (0,0,255),3)
                cv2.imshow(WINDOW_NAME, frame)
                cv2.waitKey(1)
                time.sleep(wait_after_feedback)
                break

            cv2.imshow(WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                laser.release()
                pygame.mixer.quit()
                cv2.destroyAllWindows()
                return
        current = quiz.next()

    try:
        print("Quiz finished! Score:", quiz.score,"/", quiz.index)
        final = np.zeros((WIN_H, WIN_W, 3), dtype=np.uint8)
        msg = f"Finished! Score: {quiz.score}/{quiz.index}"
        cv2.putText(final, msg, (WIN_W//2-250, WIN_H//2), cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,255,255),3)
        cv2.imshow(WINDOW_NAME, final)
        cv2.waitKey(0)
    except Exception as e:
        print(f"Error showing final score: {e}")
    finally:
        try:
            laser.release()
            pygame.mixer.quit()
            cv2.destroyAllWindows()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuiz interrupted by user")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("Waiting 3 seconds before exit...")
        time.sleep(3)
