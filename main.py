import cv2
import numpy as np
import tkinter as tk
from tkinter import Frame
from PIL import Image, ImageTk
import pyautogui

class HandTrackingApp(Frame):
    def __init__(self, window, window_title, video_source=0, width=800, height=600):
        self.previous_area = 0
        super().__init__(window)
        self.window = window
        self.window.title(window_title)

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        # Set the canvas dimensions
        self.canvas = tk.Canvas(self.window, width=width, height=height)
        self.canvas.pack()

        self.width = width
        self.height = height

        self.btn_start = tk.Button(self.window, text="Start Hand Tracking", command=self.start_tracking)
        self.btn_start.pack(side=tk.LEFT)

        self.btn_stop = tk.Button(self.window, text="Stop Hand Tracking", command=self.stop_tracking)
        self.btn_stop.pack(side=tk.LEFT)

        self.is_tracking = False

        self.update()
        self.window.mainloop()

    def start_tracking(self):
        self.is_tracking = True

    def stop_tracking(self):
        self.is_tracking = False


    def detect_hand(self, frame):
        # Convert the frame to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define a range for skin color in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        # Threshold the frame for skin color
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            current_area = cv2.contourArea(largest_contour)

            if self.previous_area - current_area > 10000:
                print("hello world")

            self.previous_area = current_area

        return frame

    def update(self):
        ret, frame = self.vid.read()

        if ret:
            frame = cv2.resize(frame, (self.width, self.height))

            if self.is_tracking:
                frame = self.detect_hand(frame)

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(10, self.update)



HandTrackingApp(tk.Tk(), "tracking hand", width=1000, height=800)
