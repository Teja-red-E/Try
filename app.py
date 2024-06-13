import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("Webcam Access Test")
webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)
