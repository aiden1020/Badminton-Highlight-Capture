import streamlit as st
import cv2
import os
from PIL import Image

st.title('Get Template')

video_folder = "Dataset/Video"

video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

if video_files:
    video_files.insert(0, "Please select video")

    selected_video = st.selectbox(
        "Select a video to play", video_files, index=0)

    if selected_video != "Please select video":
        video_path = os.path.join(video_folder, selected_video)

        seconds = st.number_input(
            "Enter the second to extract (starting from 0)", min_value=0, value=0, step=1)

        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        crop_x1 = st.slider(
            "Crop X1", min_value=0, max_value=width, value=0, step=1)
        crop_x2 = st.slider(
            "Crop X2", min_value=0, max_value=width, value=width, step=1)
        crop_y1 = st.slider(
            "Crop Y1", min_value=0, max_value=height, value=0, step=1)
        crop_y2 = st.slider(
            "Crop Y2", min_value=0, max_value=height, value=height, step=1)

        fps = cap.get(cv2.CAP_PROP_FPS)

        cap.set(cv2.CAP_PROP_POS_FRAMES, seconds * fps)

        ret, frame = cap.read()

        if ret:
            height, width, _ = frame.shape
            crop_x2 = min(crop_x2, width)
            crop_y2 = min(crop_y2, height)

            cropped_frame = frame[crop_y1:crop_y2,
                                  crop_x1:crop_x2]

            cropped_frame_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)

            frame_image = Image.fromarray(cropped_frame_rgb)

            # Display the cropped frame
            st.image(
                frame_image, caption=f"Frame at {seconds} seconds from video '{selected_video}' (Cropped)", use_column_width=True)
        else:
            st.write(
                "Unable to extract the frame; the second may exceed the total duration of the video.")
        cap.release()
else:
    st.write("No MP4 videos found in the specified folder.")
