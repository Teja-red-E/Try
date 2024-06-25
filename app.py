import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import os
from cvzone.PoseModule import PoseDetector
import cvzone
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Paths to the resources
shirt_path = "Shirts"

# Ensure resource files are in the correct path
if not os.path.exists(shirt_path):
    st.error("Resource files not found. Make sure Shirts directory is uploaded.")
    st.stop()

# Define shirt information (image filenames and prices)
shirt_info = [
    {"image": "1.png", "price": "₹500"},
    {"image": "2.png", "price": "₹750"},
    {"image": "3.png", "price": "₹600"},
    {"image": "4.png", "price": "₹500"},
    {"image": "5.png", "price": "₹750"},
    {"image": "6.png", "price": "₹600"},
]

# Initialize pose detector
detector = PoseDetector()
logging.debug("PoseDetector initialized.")

# Define the VideoProcessor class
class VideoProcessor:
    def __init__(self):
        self.counter_r = 0
        self.counter_l = 0
        self.img_num = 0
        self.shirt_info = shirt_info

    def recv(self, frame):
        logging.debug("Frame received.")
        frm = frame.to_ndarray(format="bgr24")

        img = detector.findPose(frm, draw=False)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            logging.debug(f"Landmarks detected: {lmList}")
            lm16 = lmList[16]  # Index finger landmark
            lm19 = lmList[19]  # Thumb landmark

            # Check if the index finger is within the left button region
            left_button_region = (0, 100, 176, 500)  # Adjusted for 880 width
            right_button_region = (880 - 176, 100, 176, 500)  # Adjusted for 880 width
            
            if left_button_region[0] < lm16[0] < left_button_region[0] + left_button_region[2] and \
                    left_button_region[1] < lm16[1] < left_button_region[1] + left_button_region[3]:
                self.counter_r += 1
                if self.counter_r * 7 > 360:
                    self.counter_r = 0
                    if self.img_num < len(self.shirt_info) - 1:
                        self.img_num += 1

            # Check if the thumb is within the right button region
            elif right_button_region[0] < lm19[0] < right_button_region[0] + right_button_region[2] and \
                    right_button_region[1] < lm19[1] < right_button_region[1] + right_button_region[3]:
                self.counter_l += 1
                if self.counter_l * 7 > 360:
                    self.counter_l = 0
                    if self.img_num > 0:
                        self.img_num -= 1
            else:
                self.counter_r = 0
                self.counter_l = 0

            lm11 = lmList[11][0:2]
            lm12 = lmList[12][0:2]

            imgShirt_path = os.path.join(shirt_path, self.shirt_info[self.img_num]["image"])
            logging.debug(f"Loading shirt image from: {imgShirt_path}")
            imgShirt = cv2.imread(imgShirt_path, cv2.IMREAD_UNCHANGED)

            if imgShirt is not None:
                ratio = 262 / 190  # Adjust based on your shirt dimensions
                shirt_ratio = 581 / 440  # Adjust based on your shirt dimensions
                shirt_width = int((lm11[0] - lm12[0]) * ratio)
                imgShirt = cv2.resize(imgShirt, (shirt_width, int(shirt_width * shirt_ratio)))
                scale = (lm11[0] - lm12[0]) / 190
                offset = int(44 * scale), int(48 * scale)

                try:
                    img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
                    logging.debug("Shirt overlaid on image.")
                except Exception as e:
                    st.write(f"Error overlaying image: {e}")
                    logging.error(f"Error overlaying image: {e}")
            else:
                logging.error(f"Error loading shirt image from: {imgShirt_path}")

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
    logging.debug("WebRTC streamer initialized.")

# Display shirt gallery in three columns
st.markdown("# Shirt Gallery")

# Calculate number of rows and columns for grid display
num_cols = 3
num_rows = (len(shirt_info) + num_cols - 1) // num_cols

# Distribute shirts evenly across columns
for row in range(num_rows):
    cols = st.columns(num_cols)
    for col, shirt_index in zip(cols, range(row * num_cols, (row + 1) * num_cols)):
        if shirt_index < len(shirt_info):
            shirt = shirt_info[shirt_index]
            col.image(os.path.join(shirt_path, shirt["image"]), caption=f"{shirt['price']}", width=200)
            if col.button("Try On", key=f"try_on_{shirt_index}"):
                st.session_state['selected_shirt'] = shirt_index
                st.experimental_rerun()

def try_on_shirt(shirt_index):
    st.experimental_set_query_params(shirt=shirt_index)
    st.experimental_rerun()
