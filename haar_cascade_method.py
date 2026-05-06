#open a new terminal and run .\myenv\Scripts\activate to activate the virtual environment
#then run pip install opencv-python to install the OpenCV library
#make sure to have the haar_face.xml and haar_eye.xml files in the same directory as this script
#you can download the haar cascades from OpenCV's GitHub repository

import cv2 as cv
import numpy as np
import platform
import threading
import os

# -------------------------------
# 🔊 Alarm Setup
# -------------------------------
if platform.system() == 'Windows':
    import winsound
else:
    winsound = None

alarm_on = False

def start_alarm():
    global alarm_on
    if winsound and not alarm_on:
        alarm_on = True
        # SND_LOOP keeps it ringing, SND_ASYNC keeps the code running
        winsound.PlaySound('alarm.wav', winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)

def stop_alarm():
    global alarm_on
    if winsound and alarm_on:
        winsound.PlaySound(None, winsound.SND_PURGE) # Stops the loop
        alarm_on = False

# -------------------------------
# 📂 Load Haar Cascades
# -------------------------------
face_cascade = cv.CascadeClassifier('haar_face.xml')
eye_cascade = cv.CascadeClassifier('haar_eye.xml')

# -------------------------------
# 🎥 Start Webcam
# -------------------------------
cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Set a manual FPS buffer since cap.get(cv.CAP_PROP_FPS) often returns 0 on webcams
EYE_CLOSED_SECONDS = 1.5
FPS_ESTIMATE = 15 
EYE_CLOSED_FRAMES = int(FPS_ESTIMATE * EYE_CLOSED_SECONDS)

counter = 0

# -------------------------------
# 🔁 Main Loop
# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Logic: Assume eyes are closed unless we actively find them
    eyes_detected = False

    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Search for eyes only inside the face region
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10) # Increased minNeighbors for accuracy

        if len(eyes) > 0:
            eyes_detected = True
            for (ex, ey, ew, eh) in eyes:
                cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

    # 🚨 Alarm Logic
    if not eyes_detected:
        counter += 1
        if counter >= EYE_CLOSED_FRAMES:
            cv.putText(frame, "DROWSINESS ALERT!", (50, 50),
                       cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            start_alarm()
    else:
        counter = 0
        stop_alarm()

    cv.imshow("Driver Drowsiness Detection", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# 🧹 Cleanup
stop_alarm()
cap.release()
cv.destroyAllWindows()