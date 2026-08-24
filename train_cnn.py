import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

# Đường dẫn dữ liệu
data_dir = r"E:\recording_video_car\cnn_dataset"

# Biến đổi ảnh
transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor()
])

# Load dữ liệu
dataset = datasets.ImageFolder(data_dir, transform=transform)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Danh sách nhãn
print("🧾 Danh sách nhãn:", dataset.classes)

# Mô hình CNN đơn giản
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
            nn.Linear(128, 3)  # 3 nhãn: left, center, right
        )

    def forward(self, x):
        return self.fc(self.conv(x))

# Khởi tạo model
model = LaneCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Huấn luyện
num_epochs = 10
for epoch in range(num_epochs):
    total_loss = 0
    for images, labels in dataloader:
        preds = model(images)
        loss = criterion(preds, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"✅ Epoch {epoch+1}/{num_epochs}, Loss: {total_loss:.4f}")

# Lưu mô hình
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), "models/lane_cnn_model.pt")
print("✅ Đã lưu mô hình vào: models/lane_cnn_model.pt")
