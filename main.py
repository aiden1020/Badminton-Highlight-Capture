import streamlit as st
import cv2
import os
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import numpy as np
import pandas as pd
from utilize import calculate_ssim, format_time, remove_nearby_frames, crop_video

st.title('Capture Hightlight Video')

# path
video_folder = "Dataset/Video"
output_folder = "Output"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

if video_files:
    video_files.insert(0, "--")
    selected_video = st.selectbox("Select video(mp4)", video_files, index=0)

    if selected_video != "--":

        uploaded_template = st.file_uploader(
            "upload template", type=["jpg", "jpeg", "png"])

        if uploaded_template:
            template_image = Image.open(uploaded_template)
            template_image = np.array(template_image)

            # Convert to BGR
            template_image_bgr = cv2.cvtColor(
                template_image, cv2.COLOR_RGB2BGR)

            # set to crop range
            crop_x1 = st.number_input(
                "Crop X1", min_value=0, value=480, step=1)
            crop_x2 = st.number_input(
                "Crop X2", min_value=0, value=780, step=1)
            crop_y1 = st.number_input(
                "Crop Y1", min_value=0, value=100, step=1)
            crop_y2 = st.number_input(
                "Crop Y2", min_value=0, value=520, step=1)

            # Set the ssim threshold
            ssim_threshold = st.slider(
                "SSIM threshold", min_value=0.0, max_value=1.0, value=0.85, step=0.01)

            if st.button("Go"):
                video_path = os.path.join(video_folder, selected_video)

                # video to frame
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames = int(
                    cap.get(cv2.CAP_PROP_FRAME_COUNT))

                frame_number = 0
                high_ssim_frames = []

                progress_bar = st.progress(0)

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    height, width, _ = frame.shape
                    crop_x2 = min(crop_x2, width)
                    crop_y2 = min(crop_y2, height)

                    cropped_frame = frame[crop_y1:crop_y2,
                                          crop_x1:crop_x2]

                    ssim_value = calculate_ssim(
                        cropped_frame, template_image_bgr)

                    if ssim_value >= ssim_threshold:
                        time_in_seconds = frame_number / fps
                        high_ssim_frames.append({
                            "time(s)": time_in_seconds,
                            "frame": frame_number,
                            "SSIM value": f"{ssim_value:.4f}"
                        })

                    frame_number += 1

                    progress = (frame_number / total_frames) * 100
                    progress_bar.progress(int(progress))

                cap.release()

                # delete the similar frame
                high_ssim_frames = remove_nearby_frames(high_ssim_frames)

                # show the captured time table
                if high_ssim_frames:
                    for frame in high_ssim_frames:
                        frame["time(m:s)"] = format_time(frame["time(s)"])

                    df = pd.DataFrame(high_ssim_frames)
                    st.dataframe(df[['time(m:s)', 'frame', 'SSIM value']])

                    highlight_periods = []
                    for i in range(0, len(high_ssim_frames), 2):
                        if i + 1 < len(high_ssim_frames):
                            highlight_periods.append({
                                "start (s)": high_ssim_frames[i]["time(s)"],
                                "end (s)": high_ssim_frames[i + 1]["time(s)"]
                            })

                    if highlight_periods:
                        st.write("Highlight time slots")
                        st.dataframe(pd.DataFrame(highlight_periods))

                        crop_video(
                            video_path, highlight_periods, output_folder)
                        st.write(
                            f"Highlight video output saved: {output_folder}")
                else:
                    st.write(
                        "similar picture not found, try to lower ssim threshold")
else:
    st.write("Direactory cannot found MP4 video")
