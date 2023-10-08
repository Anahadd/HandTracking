import cv2
import numpy as np
import tkinter as tk
from tkinter import Frame
from PIL import Image, ImageTk
import mediapipe as mp
import pyautogui
import time

class DigitalKeyboardApp(Frame):
    def __init__(self, window, window_title, video_source=0, width=1000, height=800):
        super().__init__(window)
        self.window = window
        self.window.title(window_title)

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(self.window, width=width, height=height)
        self.canvas.pack(pady=20)

        control_frame = tk.Frame(self.window)
        control_frame.pack(pady=20)

        self.btn_start = tk.Button(control_frame, text="Start Hand Tracking", command=self.start_tracking)
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = tk.Button(control_frame, text="Stop Hand Tracking", command=self.stop_tracking)
        self.btn_stop.grid(row=0, column=1, padx=10)

        self.is_tracking = False

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()

        self.update()
        self.window.mainloop()

    def start_tracking(self):
        self.is_tracking = True

    def stop_tracking(self):
        self.is_tracking = False

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.resize(frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
            if self.is_tracking:
                frame = self.track_hand(frame)

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(10, self.update)

    def track_hand(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                thumb_tip = [hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].x,
                             hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP].y]
                index_base = [hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP].x,
                              hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP].y]
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].x
                pinky_tip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y

                if np.linalg.norm(np.array(thumb_tip) - np.array(index_base)) < 0.05:
                    time.sleep(1)
                    pyautogui.hotkey('alt', 'shift', 'tab')
                elif thumb_tip[1] < pinky_tip_y:
                    self.stop_tracking()
                elif thumb_tip[1] > pinky_tip_y:
                    print("thumbs down")

        return frame

DigitalKeyboardApp(tk.Tk(), "Digital Keyboard App", width=1200, height=800)
