import streamlit as st
import cv2
import os
from cvzone.PoseModule import PoseDetector
import cvzone

def main():
    st.title("Virtual Dress Try-On")

    # Load button images
    button_r = cv2.imread("C:/Users/chara/Downloads/Resources-1/Resources/button.png", cv2.IMREAD_UNCHANGED)
    button_l = cv2.flip(button_r, 1)

    s_path = "C:/Users/chara/Downloads/Resources-1/Resources/Shirts"
    listShirts = os.listdir(s_path)
    ratio = 262 / 190  # width of shirt/width of points
    shirt_ratio = 581 / 440
    img_num = 0
    counter_r = 0
    counter_l = 0
    speed = 7

    # Define regions for left and right buttons
    left_button_region = (0, 100, 200, 500)  # Define the region for the left button (x, y, width, height)
    right_button_region = (1080, 100, 200, 500)  # Define the region for the right button (x, y, width, height)

    # Start webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Failed to open webcam.")
        return

    frame_width = 1280
    frame_height = 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    detector = PoseDetector()

    stframe = st.empty()

    while True:
        success, img = cap.read()
        if not success:
            st.write("Failed to capture image from webcam.")
            break

        img = detector.findPose(img, draw=False)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)
        
        if lmList:
            lm16 = lmList[16]  # Index finger landmark
            lm19 = lmList[19]  # Thumb landmark

            # Check if the index finger is within the left button region
            if left_button_region[0] < lm16[0] < left_button_region[0] + left_button_region[2] and \
                    left_button_region[1] < lm16[1] < left_button_region[1] + left_button_region[3]:
                counter_r += 1
                cv2.ellipse(img, (139, 360), (66, 66), 0, 0, counter_r * speed, (0, 255, 0), 20)
                if counter_r * speed > 360:
                    counter_r = 0
                    if img_num < len(listShirts) - 1:
                        img_num += 1

            # Check if the thumb is within the right button region
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

            imgShirt = cv2.imread(os.path.join(s_path, listShirts[img_num]), cv2.IMREAD_UNCHANGED)
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

        # Convert image for Streamlit display
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        stframe.image(img_rgb, channels="RGB", use_column_width=True)

if __name__ == "__main__":
    main()
