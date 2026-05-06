import cv2
import math
import threading
from playsound import playsound  # type: ignore[import]
import dlib  # type: ignore[import]

# ----------------------------
# EAR FUNCTION
# ----------------------------
def eye_aspect_ratio(eye):
    A = math.hypot(eye[1][0] - eye[5][0], eye[1][1] - eye[5][1])
    B = math.hypot(eye[2][0] - eye[4][0], eye[2][1] - eye[4][1])
    C = math.hypot(eye[0][0] - eye[3][0], eye[0][1] - eye[3][1])
    return (A + B) / (2.0 * C)

# ----------------------------
# Alarm

# ----------------------------
def play_alarm():
    playsound("alarm.wav")

# ----------------------------
# Load models
# ----------------------------
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

LEFT_EYE = list(range(42, 48))
RIGHT_EYE = list(range(36, 42))

# Face outline points (jawline + eyebrows + nose + mouth + eyes)
FACE_OUTLINE = list(range(0, 17)) + list(range(17, 27)) + list(range(27, 36)) + list(range(36, 48)) + list(range(48, 68))

EAR_THRESHOLD = 0.22
CONSEC_FRAMES = 10              #consecutive frames the eye must be below the threshold to trigger the alarm

counter = 0
alarm_on = False

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        shape = predictor(gray, face)
        coords = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

        left_eye = [coords[i] for i in LEFT_EYE]
        right_eye = [coords[i] for i in RIGHT_EYE]

        leftEAR = eye_aspect_ratio(left_eye)
        rightEAR = eye_aspect_ratio(right_eye)
        ear = (leftEAR + rightEAR) / 2.0

        # ----------------------------
        # Drowsiness logic
        # ----------------------------
        if ear < EAR_THRESHOLD:
            counter += 1
            color = (0, 0, 255)  # RED
            if counter >= CONSEC_FRAMES:
                cv2.putText(frame, "DROWSY ALERT!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                if not alarm_on:
                    alarm_on = True
                    threading.Thread(target=play_alarm, daemon=True).start()
        else:
            counter = 0
            alarm_on = False
            color = (0, 255, 0)  # GREEN

        # ----------------------------
        # DRAW FACE OUTLINE (GREEN)
        # ----------------------------
        for i in range(len(FACE_OUTLINE)):
            pt1 = coords[FACE_OUTLINE[i]]
            pt2 = coords[FACE_OUTLINE[(i + 1) % len(FACE_OUTLINE)]]
            cv2.line(frame, pt1, pt2, (0, 255, 0), 1)

        # ----------------------------
        # DRAW EYES (color changes)
        # ----------------------------
        def draw_eye(eye_points, clr):
            for i in range(len(eye_points)):
                pt1 = eye_points[i]
                pt2 = eye_points[(i + 1) % len(eye_points)]
                cv2.line(frame, pt1, pt2, clr, 2)

        draw_eye(left_eye, color)
        draw_eye(right_eye, color)

        # ----------------------------
        # DISPLAY EAR
        # ----------------------------
        cv2.putText(frame, f"EAR: {ear:.2f}", (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.putText(frame, f"Counter: {counter}", (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)

    cv2.imshow("Driver Monitoring System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()