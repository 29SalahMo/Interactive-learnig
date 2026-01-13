import cv2
import mediapipe as mp
import time

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

def get_attention_state(landmarks):
    left_eye = [33, 133]
    right_eye = [362, 263]

    left_open = landmarks[left_eye[1]].y - landmarks[left_eye[0]].y
    right_open = landmarks[right_eye[1]].y - landmarks[right_eye[0]].y

    eye_open_avg = (left_open + right_open) / 2

    # simple attention classifier
    if eye_open_avg > 0.020:
        return "HIGH"
    else:
        return "LOW"

cap = cv2.VideoCapture(0)

last_write_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        state = get_attention_state(lm)
    else:
        state = "NO_FACE"

    # write every 1 second
    if time.time() - last_write_time > 1:
        with open("attention_state.txt", "w") as f:
            f.write(state)
        last_write_time = time.time()

    cv2.putText(frame, f"State: {state}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Gaze Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
