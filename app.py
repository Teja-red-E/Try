import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import logging

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.logger = logging.getLogger("VideoTransformer")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.logger.debug("Frame received: shape=%s", img.shape)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("Webcam Access Test")
webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)
