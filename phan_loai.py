import cv2
import os
from pathlib import Path
import shutil

# Đường dẫn ảnh cần phân loại
UNLABELED_DIR = r"E:\recording_video_car\all_images"  # Đảm bảo đúng đường dẫn
OUTPUT_DIR = r"E:\recording_video_car\cnn_dataset"

# Tạo thư mục đích nếu chưa có
for label in ["left", "center", "right"]:
    os.makedirs(os.path.join(OUTPUT_DIR, label), exist_ok=True)
# Danh sách ảnh
images = list(Path(UNLABELED_DIR).glob("*.jpg"))
total = len(images)
batch_size = 5
i = 0

while i < total:
    batch = images[i:i+batch_size]

    for j, image_path in enumerate(batch):
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Lỗi đọc ảnh: {image_path}")
            continue

        # Thêm hướng dẫn vào ảnh
        text = f"[{j+1}/{len(batch)}] {image_path.name} - W: Center, A: Left, D: Right"
        cv2.putText(image, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Hiển thị ảnh
        cv2.imshow("Labeling Tool", image)
        key = cv2.waitKey(0)

        if key == 27:  # ESC để thoát
            cv2.destroyAllWindows()
            exit()
        elif key == ord('w'):
            label = "center"
        elif key == ord('a'):
            label = "left"
        elif key == ord('d'):
            label = "right"
        else:
            print("⛔ Phím không hợp lệ. Bỏ qua ảnh.")
            continue

        # Di chuyển ảnh vào thư mục tương ứng
        dst = os.path.join(OUTPUT_DIR, label, image_path.name)
        shutil.move(str(image_path), dst)
        print(f"✅ Đã gán nhãn [{label}] cho ảnh {image_path.name}")

    i += batch_size

cv2.destroyAllWindows()
print("🎉 Đã phân loại xong tất cả ảnh.")