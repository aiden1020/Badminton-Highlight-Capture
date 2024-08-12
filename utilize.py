import cv2
import os
from skimage.metrics import structural_similarity as ssim


def calculate_ssim(frame, template):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray_template, gray_frame, full=True)
    return score


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


# remove the duplicate time
def remove_nearby_frames(frames, threshold=3.0):
    filtered_frames = []
    last_time = -threshold
    for frame in frames:
        if (frame["time(s)"] - last_time) >= threshold:
            filtered_frames.append(frame)
            last_time = frame["time(s)"]
    return filtered_frames

# crop highlight video for ouput


def crop_video(video_path, highlight_periods, output_folder):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    for i, period in enumerate(highlight_periods):
        start_time = period["start (s)"]
        end_time = period["end (s)"]

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        output_file = os.path.join(output_folder, f"highlight_{i+1}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps,
                              (int(cap.get(3)), int(cap.get(4))))

        while True:
            ret, frame = cap.read()
            if not ret or cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
                break
            out.write(frame)

        out.release()

    cap.release()
