import streamlit as st
import cv2
import numpy as np

st.title("Webcam Access Test")

# JavaScript to access the webcam and send the frames to Streamlit
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

# Handle incoming frame from JavaScript
if 'frame' in st.session_state:
    img = st.session_state['frame']
    st.image(img, channels="BGR")

# Handle image upload endpoint
def upload():
    if st.experimental_get_query_params().get("action", [None])[0] == "upload":
        data = st.experimental_get_query_params().get("image", [None])[0]
        if data:
            # Decode the image data
            img = decode_image(data)
            st.session_state['frame'] = img
        st.stop()

# Function to decode base64 image data
def decode_image(image_data):
    image_data = image_data.split(",")[1]
    image_data = base64.b64decode(image_data)
    image_data = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    return image

# Call upload function to handle image data
upload()

if __name__ == "__main__":
    main()
