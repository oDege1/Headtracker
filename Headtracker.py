import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from tkinter import messagebox
import time

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

new_center_x = screen_w // 2
new_center_y = screen_h // 2

pyautogui.moveTo(new_center_x, new_center_y)

pyautogui.FAILSAFE = False

root = tk.Tk()

sensitivity_factor = tk.DoubleVar(root)
sensitivity_factor.set(6.0)

running = tk.BooleanVar(root)
running.set(False)


def start_stop():
    running.set(not running.get())


def update_sensitivity(val):
    sensitivity_factor.set(float(val))


start_button = tk.Button(root, text="Iniciar/Parar", command=start_stop)
start_button.pack()

sensitivity_scale = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, label="Sensibilidade", length=400,
                             sliderlength=20, variable=sensitivity_factor, command=update_sensitivity)
sensitivity_scale.pack()

eye_closed_time = 0
clicking = False

while True:
    if running.get():
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                if id == 1:
                    screen_x = new_center_x + (landmark.x - 0.5) * screen_w * sensitivity_factor.get()
                    screen_y = new_center_y + (landmark.y - 0.5) * screen_h * sensitivity_factor.get()

                    screen_x = min(max(screen_x, 0), screen_w - 1)
                    screen_y = min(max(screen_y, 0), screen_h - 1)

                    pyautogui.moveTo(screen_x, screen_y)

            left_eye = [landmarks[145], landmarks[159]]
            right_eye = [landmarks[374], landmarks[386]]

            left_eye_closed = (left_eye[0].y - left_eye[1].y) < 0.00930
            right_eye_closed = (right_eye[0].y - right_eye[1].y) < 0.00930

            if left_eye_closed and not right_eye_closed:
                if not clicking:
                    eye_closed_time = time.time()
                    clicking = True
                elif time.time() - eye_closed_time >= 0.5:
                    pyautogui.mouseDown()
            else:
                if clicking:
                    if time.time() - eye_closed_time < 0.5:
                        pyautogui.click()
                    else:
                        pyautogui.mouseUp()
                    clicking = False

        cv2.imshow('Eye Controlled Mouse', frame)
        cv2.waitKey(1)
    root.update_idletasks()
    root.update()
