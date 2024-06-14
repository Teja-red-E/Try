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

# Define regions for left and right buttons
left_button_region = (0, 100, 200, 500)  # Define the region for the left button (x, y, width, height)
right_button_region = (1080, 100, 200, 500)  # Define the region for the right button (x, y, width, height)

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
            if left_button_region[0] < lm16[0] < left_button_region[0] + left_button_region[2] and \
                    left_button_region[1] < lm16[1] < left_button_region[1] + left_button_region[3]:
                self.counter_r += 1
                cv2.ellipse(img, (139, 360), (66, 66), 0, 0, self.counter_r * 7, (0, 255, 0), 20)
                if self.counter_r > 51:
                    self.counter_r = 0
                    if self.img_num < len(self.listShirts) - 1:
                        self.img_num += 1

            # Check if the thumb is within the right button region
            elif right_button_region[0] < lm19[0] < right_button_region[0] + right_button_region[2] and \
                    right_button_region[1] < lm19[1] < right_button_region[1] + right_button_region[3]:
                self.counter_l += 1
                cv2.ellipse(img, (1138, 360), (66, 66), 0, 0, self.counter_l * 7, (0, 255, 0), 20)
                if self.counter_l > 51:
                    self.counter_l = 0
                    if self.img_num > 0:
                        self.img_num -= 1
            else:
                self.counter_r = 0
                self.counter_l = 0

            lm11 = lmList[11][0:2]
            lm12 = lmList[12][0:2]

            imgShirt = cv2.imread(os.path.join(shirt_path, self.listShirts[self.img_num]), cv2.IMREAD_UNCHANGED)
            shirt_width = int((lm11[0] - lm12[0]) * 262 / 190)
            imgShirt = cv2.resize(imgShirt, (shirt_width, int(shirt_width * 581 / 440)))
            scale = (lm11[0] - lm12[0]) / 190
            offset = int(44 * scale), int(48 * scale)

            try:
                img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            except Exception as e:
                st.write(f"Error overlaying image: {e}")

            img = cvzone.overlayPNG(img, button_r, (1074, 293))
            img = cvzone.overlayPNG(img, button_l, (72, 293))

        return av.VideoFrame.from_ndarray(img, format='bgr24')

# Add an API endpoint to serve the list of shirts
def get_shirts():
    shirts = [{'name': shirt, 'imageUrl': f'Shirts/{shirt}'} for shirt in listShirts]
    return shirts

st.set_option('deprecation.showfileUploaderEncoding', False)

# Define a route to serve the shirts data
params = st.query_params()
if 'api' in params and params['api'][0] == "shirts":
    st.write(json.dumps(get_shirts()))
    st.stop()

# Handle the try-on feature with query parameters
query_params = st.query_params()
if 'shirt' in query_params:
    st.session_state['selected_shirt'] = query_params['shirt'][0]

# Display the shirt gallery
st.markdown("# Shirt Gallery")
for shirt in listShirts:
    st.image(os.path.join(shirt_path, shirt), width=200)
    st.button("Try On", key=shirt, on_click=lambda s=shirt: try_on_shirt(s))

def try_on_shirt(shirt):
    st.session_state['selected_shirt'] = shirt
    st.query_params(shirt=shirt)
    st.experimental_rerun()

# Configure WebRTC
if 'selected_shirt' in st.session_state:
    st.markdown("# Virtual Try-On")
    webrtc_streamer(
        key="example",
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
    )
