import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import os

# Initialize PoseDetector
from cvzone.PoseModule import PoseDetector

detector = PoseDetector()

# Dummy shirt information (for testing)
shirt_info = [
    {"image": "1.png", "price": "₹500"},
    {"image": "2.png", "price": "₹750"},
    {"image": "3.png", "price": "₹600"},
]

# Dummy directory (adjust to your actual path)
shirt_path = "Shirts"

class VideoProcessor:
    def __init__(self):
        self.img_num = 0

    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")

        img = detector.findPose(frm, draw=False)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            lm11 = lmList[11][0:2]
            lm12 = lmList[12][0:2]

            imgShirt = cv2.imread(os.path.join(shirt_path, shirt_info[self.img_num]["image"]), cv2.IMREAD_UNCHANGED)
            ratio = 262 / 190
            shirt_ratio = 581 / 440
            shirt_width = int((lm11[0] - lm12[0]) * ratio)
            imgShirt = cv2.resize(imgShirt, (shirt_width, int(shirt_width * shirt_ratio)))
            scale = (lm11[0] - lm12[0]) / 190
            offset = int(44 * scale), int(48 * scale)

            try:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)  # Ensure the image has an alpha channel
                img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            except Exception as e:
                st.write(f"Error overlaying image: {e}")

        return av.VideoFrame.from_ndarray(img, format='bgr24')

# Streamlit app layout
st.title("Virtual Dress Try-On with Webcam")

# Configure WebRTC for webcam and virtual try-on
webrtc_streamer(
    key="example",
    video_processor_factory=VideoProcessor,
    rtc_configuration=RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    ),
)

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
                st.set_query_params(shirt=shirt_index)
                st.rerun()

def try_on_shirt(shirt_index):
    st.set_query_params(shirt=shirt_index)
    st.rerun()
