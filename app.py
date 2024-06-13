import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("Webcam Access Test")

    webrtc_ctx = webrtc_streamer(
        key="example",
        video_transformer_factory=VideoTransformer,
        async_transform=True,  # Set async_transform=True to avoid blocking the main thread
    )

    if not webrtc_ctx.state.playing:
        st.write("Error connecting to webcam.")
    else:
        st.write("Webcam is connected!")

if __name__ == "__main__":
    main()
