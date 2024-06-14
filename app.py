import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import os
from cvzone.PoseModule import PoseDetector
import cvzone
import json

# Ensure resource files are in the correct path
button_r_path = "button.png"
button_l_path = "button.png"
shirt_path = "Shirts"

if not os.path.exists(button_r_path) or not os.path.exists(shirt_path):
    st.error("Resource files not found. Make sure button.png and Shirts directory are uploaded.")
    st.stop()

# Load button images
try:
    button_r = cv2.imread(button_r_path, cv2.IMREAD_UNCHANGED)
    button_l = cv2.flip(button_r, 1)
except Exception as e:
    st.error(f"Error loading button images: {e}")
    st.stop()

# Load shirt images
try:
    listShirts = os.listdir(shirt_path)
except Exception as e:
    st.error(f"Error loading shirt images from directory: {e}")
    st.stop()

# Initialize pose detector
detector = PoseDetector()

# Define the VideoProcessor class
class VideoProcessor:
    def __init__(self):
        self.counter_r = 0
        self.counter_l = 0
        self.img_num = 0
        self.listShirts = listShirts

    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")

        img = detector.findPose(frm, draw=False)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            lm16 = lmList[16]  # Index finger landmark
            lm19 = lmList[19]  # Thumb landmark

            # Check if the index finger is within the left button region
            left_button_region = (0, 100, 200, 500)  # Adjust as per your frame size
            right_button_region = (875 - 200, 100, 200, 500)  # Adjust as per your frame size
            
            if left_button_region[0] < lm16[0] < left_button_region[0] + left_button_region[2] and \
                    left_button_region[1] < lm16[1] < left_button_region[1] + left_button_region[3]:
                self.counter_r += 1
                cv2.ellipse(img, (139, 360), (66, 66), 0, 0, self.counter_r * 7, (0, 255, 0), 20)
                if self.counter_r * 7 > 360:
                    self.counter_r = 0
                    if self.img_num < len(self.listShirts) - 1:
                        self.img_num += 1

            # Check if the thumb is within the right button region
            elif right_button_region[0] < lm19[0] < right_button_region[0] + right_button_region[2] and \
                    right_button_region[1] < lm19[1] < right_button_region[1] + right_button_region[3]:
                self.counter_l += 1
                cv2.ellipse(img, (1138, 360), (66, 66), 0, 0, self.counter_l * 7, (0, 255, 0), 20)
                if self.counter_l * 7 > 360:
                    self.counter_l = 0
                    if self.img_num > 0:
                        self.img_num -= 1
            else:
                self.counter_r = 0
                self.counter_l = 0

            lm11 = lmList[11][0:2]
            lm12 = lmList[12][0:2]

            imgShirt = cv2.imread(os.path.join(shirt_path, self.listShirts[self.img_num]), cv2.IMREAD_UNCHANGED)
            ratio = 262 / 190  # Adjust based on your shirt dimensions
            shirt_ratio = 581 / 440  # Adjust based on your shirt dimensions
            shirt_width = int((lm11[0] - lm12[0]) * ratio)
            imgShirt = cv2.resize(imgShirt, (shirt_width, int(shirt_width * shirt_ratio)))
            scale = (lm11[0] - lm12[0]) / 190
            offset = int(44 * scale), int(48 * scale)

            try:
                img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            except Exception as e:
                st.write(f"Error overlaying image: {e}")

            # Adjust button overlay positions for 875x660 frame
            try:
                adjusted_left_x = 72
                adjusted_right_x = 875 - 72 - button_r.shape[1]
                adjusted_y = 293
                
                img = cvzone.overlayPNG(img, button_r, (adjusted_right_x, adjusted_y))
                img = cvzone.overlayPNG(img, button_l, (adjusted_left_x, adjusted_y))
            except Exception as e:
                st.write(f"Error overlaying buttons: {e}")

        return av.VideoFrame.from_ndarray(img, format='bgr24')

# Set up Streamlit app
st.title("Virtual Dress Try-On with Webcam")

# Configure WebRTC for webcam and virtual try-on
if 'selected_shirt' in st.session_state:
    st.markdown("# Virtual Try-On")
    webrtc_streamer(
        key="example",
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
    )

# Display shirt gallery and try-on buttons
st.markdown("# Shirt Gallery")
for shirt in listShirts:
    st.image(os.path.join(shirt_path, shirt), width=200)
    if st.button("Try On", key=shirt, on_click=lambda s=shirt: try_on_shirt(s)):
        st.session_state['selected_shirt'] = shirt

def try_on_shirt(shirt):
    st.experimental_set_query_params(shirt=shirt)
    st.experimental_rerun()
