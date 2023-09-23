import cv2
import numpy as np
import tkinter as tk
from tkinter import Frame, simpledialog, messagebox
from PIL import Image, ImageTk
import pyautogui


class HandTrackingApp(Frame):
    def __init__(self, window, window_title, video_source=0, width=1000, height=800):
        self.previous_area = 0
        self.previous_area_diff = 0

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

        self.open_hand_key = "w"  # default key
        self.fist_key = "s"  # default key
        self.blink_key = "d"  # default key

        # Add buttons to set key preferences
        self.btn_open_hand = tk.Button(self.window, text="Set Open Hand Key", command=self.set_open_hand_key)
        self.btn_open_hand.pack(side=tk.LEFT)

        self.btn_fist = tk.Button(self.window, text="Set Fist Key", command=self.set_fist_key)
        self.btn_fist.pack(side=tk.LEFT)

        self.btn_blink = tk.Button(self.window, text="Set Blink Key", command=self.set_blink_key)
        self.btn_blink.pack(side=tk.LEFT)

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

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            current_area = cv2.contourArea(largest_contour)
            current_area_diff = abs(self.previous_area - current_area)

            if current_area_diff - self.previous_area_diff > 5000:
                pyautogui.press(self.blink_key)
            elif current_area > 5000:
                pyautogui.press(self.open_hand_key)
            else:
                pyautogui.press(self.fist_key)

            self.previous_area = current_area
            self.previous_area_diff = current_area_diff

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

    def set_open_hand_key(self):
        key = simpledialog.askstring("Input", "Which key for Open Hand?")
        if key and len(key) == 1:
            self.open_hand_key = key
            messagebox.showinfo("Updated", f"Open Hand key set to {key}")

    def set_fist_key(self):
        key = simpledialog.askstring("Input", "Which key for Fist?")
        if key and len(key) == 1:
            self.fist_key = key
            messagebox.showinfo("Updated", f"Fist key set to {key}")

    def set_blink_key(self):
        key = simpledialog.askstring("Input", "Which key for Blink?")
        if key and len(key) == 1:
            self.blink_key = key
            messagebox.showinfo("Updated", f"Blink key set to {key}")
            
HandTrackingApp(tk.Tk(), "Hand Tracking App", width=1000, height=800)
