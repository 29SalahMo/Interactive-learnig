# gaze_tracker.py
import cv2
import mediapipe as mp
import time
import json
import numpy as np
from collections import deque

# -------------------------
# Config / thresholds
# -------------------------
MAX_LOG_SECONDS = 3600
EYE_OPEN_THRESH = 0.20    # normalized vertical/width ratio -> eye considered "open" if > this
GAZE_LEFT_THRESH = 0.35   # relative iris position < left => looking left
GAZE_RIGHT_THRESH = 0.65  # relative iris position > right => looking right
REPORT_PATH = "gaze_report.json"

# -------------------------
# Mediapipe init
# -------------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,   # enables iris landmarks if model supports them
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# useful sets of landmarks (commonly used indices)
# eye corner indices (MediaPipe FaceMesh standard)
LEFT_EYE_OUTER = 33
LEFT_EYE_INNER = 133
RIGHT_EYE_OUTER = 362
RIGHT_EYE_INNER = 263

# some common contour points for eye (used for bounding box if needed)
LEFT_EYE_CONTOUR = [33, 160, 158, 133, 153, 144, 145, 163]
RIGHT_EYE_CONTOUR = [362, 387, 385, 263, 373, 380, 374, 386]

# iris landmark groups used by MediaPipe when refine_landmarks=True
# (model uses indices around 468-479 for iris; different resources show 468-473/474-478 etc.)
RIGHT_IRIS = [469, 470, 471, 472]   # typically right iris
LEFT_IRIS =  [474, 475, 476, 477]   # typically left iris
# note: if these indices are not present, code will fallback to eye contour centroid

# -------------------------
# Helpers
# -------------------------
def lm_to_point(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

def get_centroid(points):
    arr = np.array(points)
    if len(arr) == 0:
        return None
    return tuple(np.mean(arr, axis=0))

def safe_get_landmark(landmarks, idx):
    try:
        return landmarks[idx]
    except Exception:
        return None

def compute_eye_box(landmarks, indices, w, h):
    pts = []
    for i in indices:
        lm = safe_get_landmark(landmarks, i)
        if lm:
            pts.append([lm.x * w, lm.y * h])
    if not pts:
        return None
    pts = np.array(pts)
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)
    return int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min), pts

# estimate iris center robustly (try iris landmarks first, fallback to eye contour centroid)
def estimate_iris_center(landmarks, iris_indices, eye_contour_indices, w, h):
    pts = []
    for i in iris_indices:
        lm = safe_get_landmark(landmarks, i)
        if lm:
            pts.append([lm.x * w, lm.y * h])
    if pts:
        cx, cy = get_centroid(pts)
        return (float(cx), float(cy)), 1.0  # confidence 1.0 because iris landmarks used

    # fallback -> use contour centroid
    pts = []
    for i in eye_contour_indices:
        lm = safe_get_landmark(landmarks, i)
        if lm:
            pts.append([lm.x * w, lm.y * h])
    if pts:
        cx, cy = get_centroid(pts)
        return (float(cx), float(cy)), 0.5  # lower confidence
    return None, 0.0

# compute relative horizontal position of iris between eye inner and outer corners [0..1]
def iris_position_relative(iris_x, outer_x, inner_x):
    left = min(outer_x, inner_x)
    right = max(outer_x, inner_x)
    if right - left <= 1e-6:
        return 0.5
    return (iris_x - left) / (right - left)

# compute simple eye open ratio: (vertical span of eye contour) / (horizontal span)
def eye_open_ratio(pts):
    pts = np.array(pts)
    if pts.size == 0:
        return 0.0
    xs = pts[:,0]
    ys = pts[:,1]
    width = xs.max() - xs.min() if xs.max() - xs.min() > 1e-6 else 1.0
    height = ys.max() - ys.min()
    return float(height / width)

# -------------------------
# Main loop & logging
# -------------------------
def run_gaze_tracker(cam_index=0, show_window=True, max_seconds=300):
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("ERROR: cannot open camera")
        return

    log = []
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h, w = frame.shape[:2]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(frame_rgb)
        gaze_direction = "unknown"
        attention = 0
        conf = {"left_conf":0.0, "right_conf":0.0}

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            # estimate left iris, right iris
            left_iris_center, left_conf = estimate_iris_center(landmarks, LEFT_IRIS, LEFT_EYE_CONTOUR, w, h)
            right_iris_center, right_conf = estimate_iris_center(landmarks, RIGHT_IRIS, RIGHT_EYE_CONTOUR, w, h)
            conf["left_conf"] = left_conf
            conf["right_conf"] = right_conf

            # compute eye boxes & contour pts
            left_box = compute_eye_box(landmarks, LEFT_EYE_CONTOUR, w, h)
            right_box = compute_eye_box(landmarks, RIGHT_EYE_CONTOUR, w, h)

            # compute open ratio (use contour pts if available)
            left_ratio = eye_open_ratio(left_box[4]) if left_box else 0.0
            right_ratio = eye_open_ratio(right_box[4]) if right_box else 0.0
            eye_open_avg = (left_ratio + right_ratio) / 2.0

            # attention heuristic: eyes open (above threshold)
            attention = 1 if eye_open_avg > EYE_OPEN_THRESH else 0

            # decide gaze using iris centers if available (prefer averaged position)
            gaze_scores = []
            if left_iris_center and left_box:
                # relative pos in left eye (0=left,1=right)
                rel_l = iris_position_relative(left_iris_center[0], left_box[0], left_box[0] + left_box[2])
                gaze_scores.append(rel_l)
                # draw left markers
                cv2.circle(frame, (int(left_iris_center[0]), int(left_iris_center[1])), 3, (0,255,255), -1)
                cv2.rectangle(frame, (left_box[0], left_box[1]), (left_box[0]+left_box[2], left_box[1]+left_box[3]), (100,100,255), 1)

            if right_iris_center and right_box:
                rel_r = iris_position_relative(right_iris_center[0], right_box[0], right_box[0] + right_box[2])
                gaze_scores.append(rel_r)
                cv2.circle(frame, (int(right_iris_center[0]), int(right_iris_center[1])), 3, (0,255,255), -1)
                cv2.rectangle(frame, (right_box[0], right_box[1]), (right_box[0]+right_box[2], right_box[1]+right_box[3]), (100,100,255), 1)

            if gaze_scores:
                avg_rel = sum(gaze_scores) / len(gaze_scores)
                if avg_rel < GAZE_LEFT_THRESH:
                    gaze_direction = "left"
                elif avg_rel > GAZE_RIGHT_THRESH:
                    gaze_direction = "right"
                else:
                    gaze_direction = "center"
            else:
                gaze_direction = "center"

            # draw some overlays
            cv2.putText(frame, f"Gaze: {gaze_direction}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0),2)
            cv2.putText(frame, f"Attention: {attention}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,0),2)
            cv2.putText(frame, f"EyeRatio: {eye_open_avg:.2f}", (10,110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,200),2)

        else:
            cv2.putText(frame, "No face detected", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255),2)

        # show
        if show_window:
            cv2.imshow("Gaze Tracker", frame)
        # log
        log.append({
            "t": round(time.time() - start_time, 2),
            "gaze": gaze_direction,
            "attention": int(attention),
            "conf": conf
        })

        # exit conditions
        if show_window:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        if max_seconds and (time.time() - start_time) > max_seconds:
            break

    cap.release()
    if show_window:
        cv2.destroyAllWindows()

    # write report
    with open(REPORT_PATH, "w") as f:
        json.dump(log, f, indent=2)
    print(f"Saved gaze report -> {REPORT_PATH}")
    return log

if __name__ == "__main__":
    run_gaze_tracker(cam_index=0, show_window=True, max_seconds=0)  # max_seconds=0 -> run until 'q'
