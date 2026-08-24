import cv2
import os
from pathlib import Path

# Đường dẫn chứa video
video_folder = r"E:\recording_video_car\nhieu"  # Đảm bảo đúng đường dẫn
output_base = r"E:\recording_video_car\all_images"
os.makedirs(output_base, exist_ok=True)

# Lặp qua tất cả các file .avi trong thư mục
video_files = list(Path(video_folder).glob("*.avi"))
frame_count = 0

for video_path in video_files:
    # Mở video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ Không thể mở video: {video_path}")
        continue

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Lưu từng frame dưới dạng ảnh trong thư mục output_base
        frame_name = os.path.join(output_base, f"frame_{frame_count:05}.jpg")
        cv2.imwrite(frame_name, frame)
        frame_count += 1

    cap.release()
    print(f"✅ Đã tách {frame_count} ảnh từ video {video_path.name} vào thư mục {output_base}")

print("🎉 Đã tách và lưu tất cả ảnh vào thư mục:", output_base)
