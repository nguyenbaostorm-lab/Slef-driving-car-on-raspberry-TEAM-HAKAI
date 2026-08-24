# ps5_camera_record.py with PID control and camera preview
# ---
# Robot xe tự hành - Điều khiển bằng tay cầm PS5, ghi video camera để huấn luyện AI + PID điều hướng
# ---

import RPi.GPIO as GPIO
from evdev import InputDevice, ecodes
import time
import os
import cv2
from picamera2 import Picamera2

# ======= THIẾT LẬP CƠ BẢN =======
gamepad = InputDevice('/dev/input/event2')

ENA, IN1, IN2 = 22, 17, 27
ENB, IN3, IN4 = 23, 24, 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)
pwmA = GPIO.PWM(ENA, 100)
pwmB = GPIO.PWM(ENB, 100)
pwmA.start(0)
pwmB.start(0)

speed = 30
speed_step = 5
l1_pressed = False
joystick_threshold = 20
recording_left = False
recording_right = False
out_left = None
out_right = None

# ======= ĐƯỜNG DẪN LƯU VIDEO =======
output_dir = "/home/pistorm/Documents/data_recoding"
os.makedirs(output_dir, exist_ok=True)

# ======= CAMERA (Picamera2) =======
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (480, 240)})
picam2.configure(config)
time.sleep(1)
picam2.start()

# ======= PID Controller =======
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

pid = PIDController(kp=0.15, ki=0.005, kd=0.03)

# ======= CÁC HÀM ĐIỀU KHIỂN XE =======
def stop():
    GPIO.output([IN1, IN2, IN3, IN4], GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)
    print("🛑 DỪNG XE")

def apply_pid_control(output):
    left_speed = speed - output
    right_speed = speed + output
    left_speed = max(0, min(100, left_speed))
    right_speed = max(0, min(100, right_speed))

    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(left_speed)
    pwmB.ChangeDutyCycle(right_speed)
    print(f"🧭 PID | L:{left_speed:.1f}% R:{right_speed:.1f}%")

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)
    print(f"⬆️ TIẾN - {speed}%")

def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)
    print(f"⬇️ LÙI - {speed}%")

def left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)
    print(f"⬅️ TRÁI - {speed}%")

def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwmA.ChangeDutyCycle(speed)
    pwmB.ChangeDutyCycle(speed)
    print(f"➡️ PHẢI - {speed}%")

def increase_speed():
    global speed
    speed = min(speed + speed_step, 100)
    print(f"⚡ Tăng tốc: {speed}%")

def decrease_speed():
    global speed
    speed = max(speed - speed_step, 0)
    print(f"🐢 Giảm tốc: {speed}%")

# ======= GHI VIDEO CAMERA =======
def start_video_recording(side):
    global recording_left, recording_right, out_left, out_right
    filename = os.path.join(output_dir, f"video_{side}_{int(time.time())}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, 15.0, (480, 240))
    if side == "left":
        out_left = out
        recording_left = True
        print(f"📹 Ghi video bên trái: {filename}")
    else:
        out_right = out
        recording_right = True
        print(f"📹 Ghi video bên phải: {filename}")

def stop_video_recording(side):
    global recording_left, recording_right, out_left, out_right
    if side == "left" and recording_left:
        out_left.release()
        recording_left = False
        print("🛑 Dừng ghi video trái")
    elif side == "right" and recording_right:
        out_right.release()
        recording_right = False
        print("🛑 Dừng ghi video phải")

# ======= HƯỚNG DẪN =======
print("""
🎮 PS5 XE ĐIỀU KHIỂN - GHI VIDEO + PID
❌ X: Tiến | ⭕ O: Lùi | ☐: Trái | △: Phải
⬆️/⬇️: Tăng/Giảm tốc độ
L1 + ⬅️: Ghi video trái | ➡️: Ghi video phải
L2: Dừng video trái    | R2: Dừng video phải
R1: ⛔ DỪNG TOÀN BỘ (xe + ghi)
""")

try:
    dx = dy = 0
    for event in gamepad.read_loop():
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

        if recording_left:
            out_left.write(frame)
        if recording_right:
            out_right.write(frame)

        cv2.imshow("Robot Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if event.type == ecodes.EV_KEY:
            if event.code == 310:
                l1_pressed = (event.value == 1)
            elif event.code == 311 and event.value == 1:
                stop()
                stop_video_recording("left")
                stop_video_recording("right")
            elif event.code == 307 and event.value == 1:
                forward()
            elif event.code == 304 and event.value == 1:
                backward()
            elif event.code == 305 and event.value == 1:
                left()
            elif event.code == 308 and event.value == 1:
                right()
            elif event.code in [304, 305, 307, 308] and event.value == 0:
                stop()

        elif event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_HAT0Y:
                if event.value == -1:
                    increase_speed()
                elif event.value == 1:
                    decrease_speed()
            elif event.code == ecodes.ABS_HAT0X:
                if l1_pressed:
                    if event.value == -1:
                        start_video_recording("left")
                    elif event.value == 1:
                        start_video_recording("right")
            elif event.code == ecodes.ABS_X:
                dx = event.value - 128
            elif event.code == ecodes.ABS_Y:
                dy = event.value - 128

            if abs(dx) < joystick_threshold and abs(dy) < joystick_threshold:
                stop()
            elif abs(dy) > abs(dx):
                if dy < -joystick_threshold:
                    forward()
                elif dy > joystick_threshold:
                    backward()
            else:
                output = pid.compute(dx)
                apply_pid_control(output)

except KeyboardInterrupt:
    stop()
    stop_video_recording("left")
    stop_video_recording("right")
    GPIO.cleanup()
    cv2.destroyAllWindows()
    print("🛑 Dừng thủ công")
