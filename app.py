import streamlit as st
from streamlit_webrtc import webrtc_streamer

def main():
    st.title("Minimal Webcam Access Test")

    webrtc_ctx = webrtc_streamer(key="example")

    if webrtc_ctx.state.playing:
        st.write("Webcam is connected!")
    else:
        st.write("Error connecting to webcam.")

if __name__ == "__main__":
    main()
