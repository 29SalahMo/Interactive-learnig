# laser_detector.py
import cv2
import numpy as np
import time

# ============================
# Laser color ranges (HSV)
# ============================
lower_red1 = np.array([0, 150, 150])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 150, 150])
upper_red2 = np.array([180, 255, 255])

lower_green = np.array([50, 150, 150])
upper_green = np.array([70, 255, 255])

def detect_laser_zone(x, frame_width):

    if x < frame_width * 0.33:
        return "LEFT"
    elif x < frame_width * 0.66:
        return "CENTER"
    else:
        return "RIGHT"

def start_laser_tracking(callback_on_detect):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_width = frame.shape[1]

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        mask = mask_red | mask_green

        mask = cv2.GaussianBlur(mask, (7, 7), 0)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        laser_point = None

        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 80:
                x, y, w, h = cv2.boundingRect(largest)
                cx = int(x + w / 2)
                cy = int(y + h / 2)
                laser_point = (cx, cy)
                cv2.circle(frame, (cx, cy), 6, (0, 255, 0), -1)


                zone = detect_laser_zone(cx, frame_width)
                callback_on_detect(zone)

        cv2.imshow("Laser Tracking", frame)
        cv2.imshow("Laser Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
