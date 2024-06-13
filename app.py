import streamlit as st
import cv2
from PIL import Image

def main():
    st.title("Webcam Access Test")

    # Start webcam capture
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Failed to open webcam.")
        return

    while True:
        success, img = cap.read()
        if not success:
            st.error("Failed to capture image from webcam.")
            break

        # Display the webcam feed
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        st.image(Image.fromarray(img_rgb), caption='Webcam', use_column_width=True)

    cap.release()

if __name__ == "__main__":
    main()
