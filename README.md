# 🚗 Autonomous Self-Driving Car on Raspberry Pi (Team Hakai)
> **Hệ thống Xe Tự Hành & Điều Khiển Động Cơ 4 Bánh (4WD) Tích Hợp Camera Thị Giác Máy Tính trên Raspberry Pi**  
> **Nền tảng:** Raspberry Pi OS, Python 3, OpenCV, PiCamera, RPi.GPIO  
> **Nhóm phát triển:** Team HAKAI | **Tác giả:** MR_STORM

---

## 📖 1. Tổng quan Dự án

Dự án xây dựng nền tảng xe robot thông minh 4 bánh dẫn động độc lập (**4-Wheel Drive - 4WD**) sử dụng máy tính nhúng **Raspberry Pi**. Hệ thống tích hợp camera quang học thời gian thực (**Raspberry Pi Camera Module**), xử lý hình ảnh qua **OpenCV**, điều khiển vận tốc & hướng lái bằng xung băm **PWM**, và sẵn sàng cho các mô hình thị giác máy tính / học máy (Machine Learning) để nhận diện làn đường và tự động di chuyển.

---

## 🛠️ 2. Sơ đồ Chân Phần cứng (Hardware Pinout & Wiring)

Hệ thống điều khiển 4 động cơ DC độc lập thông qua mạch cầu H (L298N / L9110S) kết nối với các chân GPIO của Raspberry Pi:

### Bảng cấu hình chân điều khiển 4 Động cơ (Motor Pinout - BCM Mode):

| Động cơ (Motor) | Vị trí trên xe | Chân Enable (PWM) | Chân Input 1 (IN1) | Chân Input 2 (IN2) |
| :--- | :--- | :--- | :--- | :--- |
| **Motor 1** | Bánh Trước - Trái (Front Left) | `GPIO 17` | `GPIO 27` | `GPIO 22` |
| **Motor 2** | Bánh Trước - Phải (Front Right) | `GPIO 23` | `GPIO 24` | `GPIO 25` |
| **Motor 3** | Bánh Sau - Trái (Rear Left) | `GPIO 5` | `GPIO 6` | `GPIO 13` |
| **Motor 4** | Bánh Sau - Phải (Rear Right) | `GPIO 19` | `GPIO 26` | `GPIO 21` |

> 📌 *Tần số băm xung PWM:* **100 Hz - 1 kHz** (điều chỉnh tốc độ mượt mà từ 0% đến 100% Duty Cycle).

---

## 🎮 3. Giao diện & Phím Điều khiển (Teleoperation & Camera View)

Khi chạy script `motor_camera_control.py`, luồng video từ PiCamera độ phân giải **640x480 @ 30 FPS** sẽ hiển thị trực tiếp lên màn hình OpenCV cùng với các phím tắt điều khiển:

| Phím (Key) | Hành vi của xe (Action) | Trạng thái 4 Bánh xe |
| :---: | :--- | :--- |
| **`W`** | Chạy **TIẾN** (Forward) | Cả 4 bánh quay tiến cùng tốc độ |
| **`S`** | Chạy **LÙI** (Backward) | Cả 4 bánh quay lùi |
| **`A`** | Quay **TRÁI** (Turn Left) | Bánh trái quay lùi, bánh phải quay tiến |
| **`D`** | Quay **PHẢI** (Turn Right) | Bánh trái quay tiến, bánh phải quay lùi |
| **`Space`** | **DỪNG** xe khẩn cấp (Brake/Stop) | Đưa xung PWM về 0% |
| **`Q`** | **THOÁT** chương trình | Tự động giải phóng camera và GPIO cleanup |

---

## 🧠 4. Cấu trúc Module & Mã Nguồn
