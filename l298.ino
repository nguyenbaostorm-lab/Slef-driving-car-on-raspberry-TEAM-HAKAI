#include <BluetoothSerial.h>

// === CHÂN ĐIỀU KHIỂN ===
// Motor A (trái)
const int IN1 = 26;
const int IN2 = 27;
const int ENA = 14;   // Bật HIGH để chạy full tốc độ

// Motor B (phải)
const int IN3 = 32;
const int IN4 = 33;
const int ENB = 13;   // Bật HIGH để chạy full tốc độ

BluetoothSerial SerialBT;
String device_name = "MERC_ROBOT";

// === KHAI BÁO HÀM ===
void moveForward();
void moveBackward();
void turnLeft();
void turnRight();
void stopMotors();
void processCommand(String command);

void setup() {
  Serial.begin(115200);
  SerialBT.begin(device_name); // Tên Bluetooth

  // Khai báo output
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  // Khởi động với động cơ dừng
  stopMotors();
}

void loop() {
  if (SerialBT.available()) {
    String command = SerialBT.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String command) {
  command.trim();
  Serial.print("Nhận lệnh: ");
  Serial.println(command);

  if (command.startsWith("M")) {
    switch (command.charAt(1)) {
      case '0': stopMotors(); break;
      case '1': moveBackward(); break;
      case '2': moveForward(); break;
      case '3': turnLeft(); break;
      case '4': turnRight(); break;
      default: Serial.println("⚠️ Lệnh không hợp lệ!"); break;
    }
  }
}

// === HÀM ĐIỀU KHIỂN ===
void stopMotors() {
  digitalWrite(ENA, LOW);
  digitalWrite(ENB, LOW);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void moveForward() {
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnLeft() {
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}
