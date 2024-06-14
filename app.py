import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2

# Ensure the cascade file is in the correct path
cascade_path = "haarcascade_frontalface_default.xml"
cascade = cv2.CascadeClassifier(cascade_path)

# Define the VideoProcessor class
class VideoProcessor:
    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")

        # Detect faces
        gray = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.1, 3)

        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frm, (x, y), (x+w, y+h), (0, 255, 0), 3)

        return av.VideoFrame.from_ndarray(frm, format='bgr24')

# Set up Streamlit app
st.title("Face Detection with Webcam")

# Configure WebRTC
webrtc_streamer(
    key="key",
    video_processor_factory=VideoProcessor,
    rtc_configuration=RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    ),
)

if __name__ == "__main__":
    main()
