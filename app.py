import streamlit as st
import cv2
import numpy as np
import base64
from cvzone.PoseModule import PoseDetector
import cvzone
import os

# Function to decode base64 image
def decode_image(image_data):
    image_data = image_data.split(",")[1]
    image_data = base64.b64decode(image_data)
    image_data = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    return image

def main():
    st.title("Virtual Dress Try-On")

    # Load button images
    button_r_path = "static/button.png"
    button_l_path = "static/button.png"
    shirt_path = "static/Shirts"

    button_r = cv2.imread(button_r_path, cv2.IMREAD_UNCHANGED)
    button_l = cv2.flip(button_r, 1)

    listShirts = os.listdir(shirt_path)
    ratio = 262 / 190
    shirt_ratio = 581 / 440
    img_num = 0
    counter_r = 0
    counter_l = 0
    speed = 7

    left_button_region = (0, 100, 200, 500)
    right_button_region = (1080, 100, 200, 500)

    detector = PoseDetector()

    stframe = st.empty()

    st.markdown(
        """
        <style>
        video {
            display: none;
        }
        </style>
        <video id="inputVideo" autoplay></video>
        <canvas id="canvas" style="display: none;"></canvas>
        <script>
        const video = document.getElementById('inputVideo');
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
            });

        video.addEventListener('play', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            setInterval(() => {
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/png');
                fetch('/upload', {
                    method: 'POST',
                    body: JSON.stringify({ image: imageData }),
                    headers: { 'Content-Type': 'application/json' }
                });
            }, 100);
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    # Process received frames
    if 'frame' in st.session_state:
        img = decode_image(st.session_state['frame'])
        img = detector.findPose(img, draw=False)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            lm16 = lmList[16]
            lm19 = lmList[19]

            if left_button_region[0] < lm16[0] < left_button_region[0] + left_button_region[2] and \
                    left_button_region[1] < lm16[1] < left_button_region[1] + left_button_region[3]:
                counter_r += 1
                cv2.ellipse(img, (139, 360), (66, 66), 0, 0, counter_r * speed, (0, 255, 0), 20)
                if counter_r * speed > 360:
                    counter_r = 0
                    if img_num < len(listShirts) - 1:
                        img_num += 1
            elif right_button_region[0] < lm19[0] < right_button_region[0] + right_button_region[2] and \
                    right_button_region[1] < lm19[1] < right_button_region[1] + right_button_region[3]:
                counter_l += 1
                cv2.ellipse(img, (1138, 360), (66, 66), 0, 0, counter_l * speed, (0, 255, 0), 20)
                if counter_l * speed > 360:
                    counter_l = 0
                    if img_num > 0:
                        img_num -= 1
            else:
                counter_r = 0
                counter_l = 0

            lm11 = lmList[11][0:2]
            lm12 = lmList[12][0:2]

            imgShirt = cv2.imread(os.path.join(shirt_path, listShirts[img_num]), cv2.IMREAD_UNCHANGED)
            shirt_width = int((lm11[0] - lm12[0]) * ratio)
            imgShirt = cv2.resize(imgShirt, (shirt_width, int(shirt_width * shirt_ratio)))
            scale = (lm11[0] - lm12[0]) / 190
            offset = int(44 * scale), int(48 * scale)

            try:
                img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            except Exception as e:
                st.write(f"Error overlaying image: {e}")

            img = cvzone.overlayPNG(img, button_r, (1074, 293))
            img = cvzone.overlayPNG(img, button_l, (72, 293))

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        stframe.image(img_rgb, channels="RGB", use_column_width=True)

if __name__ == "__main__":
    main()
