import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import os
import time
from cvzone.PoseModule import PoseDetector
import cvzone

# Ensure resource files are in the correct path
button_r_path = "button.png"
button_l_path = "button.png"
shirt_path = "Shirts"

if not os.path.exists(button_r_path) or not os.path.exists(shirt_path):
    st.error("Resource files not found. Make sure button.png and Shirts directory are uploaded.")
    st.stop()

# Load button images
button_r = cv2.imread(button_r_path, cv2.IMREAD_UNCHANGED)
button_l = cv2.flip(button_r, 1)

listShirts = os.listdir(shirt_path)
ratio = 262 / 190  # width of shirt/width of points
shirt_ratio = 581 / 440
speed = 7

# Define regions for left and right buttons
left_button_region = (0, 100, 200, 500)  # Define the region for the left button (x, y, width, height)
right_button_region = (1080, 100, 200, 500)  # Define the region for the right button (x, y, width, height)

# Initialize pose detector
detector = PoseDetector()

# Define the VideoProcessor class
class VideoProcessor:
    def __init__(self):
        self.counter_r = 0
        self.counter_l = 0
        self.img_num = 0
        self.listShirts = listShirts
        self.last_frame_time = time.time()

    def recv(self, frame):
        current_time = time.time()
        frame_interval = 1 / 15  # Target 15 FPS

        if current_time - self.last_frame_time < frame_interval:
            return frame  # Skip processing to maintain target frame rate

        self.last_frame_time = current_time
        frm = frame.to_ndarray(format="bgr24")

        # Log frame processing start
        print("Processing frame...")

        img = detector.findPose(frm, draw=False)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            lm16 = lmList[16]  # Index finger landmark
            lm19 = lmList[19]  # Thumb landmark

            # Check if the index finger is within the left button region
            if left_button_region[0] < lm16[0] < left_button_region[0] + left_button_region[2] and \
                    left_button_region[1] < lm16[1] < left_button_region[1] + left_button_region[3]:
                self.counter_r += 1
                cv2.ellipse(img, (139, 360), (66, 66), 0, 0, self.counter_r * speed, (0, 255, 0), 20)
                if self.counter_r * speed > 360:
                    self.counter_r = 0
                    if self.img_num < len(self.listShirts) - 1:
                        self.img_num += 1

            # Check if the thumb is within the right button region
            elif right_button_region[0] < lm19[0] < right_button_region[0] + right_button_region[2] and \
                    right_button_region[1] < lm19[1] < right_button_region[1] + right_button_region[3]:
                self.counter_l += 1
                cv2.ellipse(img, (1138, 360), (66, 66), 0, 0, self.counter_l * speed, (0, 255, 0), 20)
                if self.counter_l * speed > 360:
                    self.counter_l = 0
                    if self.img_num > 0:
       
