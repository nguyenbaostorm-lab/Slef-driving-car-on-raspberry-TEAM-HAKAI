import cv2
import torch
import torchvision.transforms as transforms
import torch.nn as nn
from PIL import Image

# 🧠 Mô hình CNN giống như đã huấn luyện
class LaneCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32*16*16, 128), nn.ReLU(),
            nn.Linear(128, 3)
        )

    def forward(self, x):
        return self.fc(self.conv(x))

# ✅ Load model đã huấn luyện
model = LaneCNN()
model.load_state_dict(torch.load("models/lane_cnn_model.pt"))
model.eval()

# Danh sách nhãn (dựa theo thứ tự thư mục training)
labels = ["center", "left", "right"]  # Cập nhật đúng thứ tự nếu cần

# 🎞️ Đường dẫn video cần test
video_path = r"E:\recording_video_car\giua\video_left_1752229906.avi"
cap = cv2.VideoCapture(video_path)

# Biến đổi ảnh
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((64, 64)),
    transforms.ToTensor()
])

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Cắt phần giữa ảnh để focus vào làn đường (tùy chọn)
    h, w, _ = frame.shape
    cropped = frame[int(h*0.4):h, int(w*0.2):int(w*0.8)]

    # Chuyển ảnh thành tensor
    img_tensor = transform(cropped).unsqueeze(0)

    # Dự đoán hướng
    with torch.no_grad():
        output = model(img_tensor)
        pred = torch.argmax(output, dim=1).item()
        direction = labels[pred]

    # Hiển thị kết quả
    cv2.putText(frame, f"du doan dieu khien: {direction}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Video Dự đoán CNN", frame)

    # Nhấn ESC để thoát
    if cv2.waitKey(25) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
