import streamlit as st
import cv2

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
        st.image(img, channels="BGR")

    cap.release()

if __name__ == "__main__":
    main()
