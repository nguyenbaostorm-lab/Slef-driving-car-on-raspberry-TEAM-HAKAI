import evdev
import time
from gpiozero import PWMOutputDevice

# ==============================
# ? MOTOR SETUP (PWM)
# ==============================
PWM_FREQUENCY = 1000  
DEFAULT_SPEED = 80  
MAX_SPEED = 98  
MIN_SPEED = 80  

# Define GPIO pins for motors
MOTORS = {
    "Back Left (M1)": (PWMOutputDevice(26, frequency=PWM_FREQUENCY), PWMOutputDevice(19, frequency=PWM_FREQUENCY)),
    "Front Left (M2)": (PWMOutputDevice(13, frequency=PWM_FREQUENCY), PWMOutputDevice(6, frequency=PWM_FREQUENCY)),
    "Back Right (M3)": (PWMOutputDevice(5, frequency=PWM_FREQUENCY), PWMOutputDevice(11, frequency=PWM_FREQUENCY)),
    "Front Right (M4)": (PWMOutputDevice(9, frequency=PWM_FREQUENCY), PWMOutputDevice(10, frequency=PWM_FREQUENCY)),
}


# ==============================
# ? PS4 Button Mapping
# ==============================
BTN_X = 304  # Cross (X) button -> Rotate Left
BTN_O = 305  # Circle (O) button -> Rotate Right
BTN_SQUARE = 308  # Square button
BTN_TRIANGLE = 307  # Triangle button
# ==============================
# ? MOTOR CONTROL FUNCTIONS
# ==============================

def set_motor(motor_pins, speed):
    pwm_a, pwm_b = motor_pins
    pwm_value = abs(speed) / 100.0  

    if speed > 0:
        pwm_a.value = pwm_value
        pwm_b.value = 0
    elif speed < 0:
        pwm_a.value = 0
        pwm_b.value = pwm_value
    else:
        pwm_a.value = 0
        pwm_b.value = 0

def stop_all_motors():
    for motor_pins in MOTORS.values():
        set_motor(motor_pins, 0)

def move_forward(speed):
    set_motor(MOTORS["Front Left (M2)"], speed)
    set_motor(MOTORS["Front Right (M4)"], speed)
    set_motor(MOTORS["Back Left (M1)"], speed)
    set_motor(MOTORS["Back Right (M3)"], speed)

def move_backward(speed):
    set_motor(MOTORS["Front Left (M2)"], -speed)
    set_motor(MOTORS["Front Right (M4)"], -speed)
    set_motor(MOTORS["Back Left (M1)"], -speed)
    set_motor(MOTORS["Back Right (M3)"], -speed)

def strafe_left(speed):
    set_motor(MOTORS["Front Left (M2)"], -speed)
    set_motor(MOTORS["Front Right (M4)"], speed)
    set_motor(MOTORS["Back Left (M1)"], speed)
    set_motor(MOTORS["Back Right (M3)"], -speed)

def strafe_right(speed):
    set_motor(MOTORS["Front Left (M2)"], speed)
    set_motor(MOTORS["Front Right (M4)"], -speed)
    set_motor(MOTORS["Back Left (M1)"], -speed)
    set_motor(MOTORS["Back Right (M3)"], speed)

def rotate_left(speed):
    set_motor(MOTORS["Front Left (M2)"], -speed)
    set_motor(MOTORS["Front Right (M4)"], speed)
    set_motor(MOTORS["Back Left (M1)"], -speed)
    set_motor(MOTORS["Back Right (M3)"], speed)

def rotate_right(speed):
    set_motor(MOTORS["Front Left (M2)"], speed)
    set_motor(MOTORS["Front Right (M4)"], -speed)
    set_motor(MOTORS["Back Left (M1)"], speed)
    set_motor(MOTORS["Back Right (M3)"], -speed)

def move_diagonal_front_left(speed):
    set_motor(MOTORS["Front Right (M4)"], speed)
    set_motor(MOTORS["Back Left (M1)"], speed)

def move_diagonal_front_right(speed):
    set_motor(MOTORS["Front Left (M2)"], speed)
    set_motor(MOTORS["Back Right (M3)"], speed)

def move_diagonal_back_right(speed):
    set_motor(MOTORS["Front Right (M4)"], -speed)
    set_motor(MOTORS["Back Left (M1)"], -speed)

def move_diagonal_back_left(speed):
    set_motor(MOTORS["Front Left (M2)"], -speed)
    set_motor(MOTORS["Back Right (M3)"], -speed)
    
    
# ==============================
# ? FIND PS4 CONTROLLER
# ==============================
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
ps4_controller = None

for device in devices:
    print(f"Found: {device.name} at {device.path}")
    if "Wireless Controller" in device.name:
        ps4_controller = evdev.InputDevice(device.path)
        break

if ps4_controller is None:
    print("PS4 Controller not found! Check Bluetooth connection.")
    exit()

print(f"Listening for input from {ps4_controller.path}...\n")

# ==============================
# ? MAIN LOOP
# ==============================

try:
    speed = DEFAULT_SPEED
    button_states = {}

    for event in ps4_controller.read_loop():
        if event.type in [evdev.ecodes.EV_KEY, evdev.ecodes.EV_ABS]:
            event_code = evdev.ecodes.bytype[event.type].get(event.code, f"UNKNOWN_{event.code}")
            event_value = event.value
            button_states[str(event_code)] = event_value

            # Get active buttons
            active_buttons = [key for key, value in button_states.items() if value != 0]

            # STOP ALL MOTORS IF NO BUTTONS ARE PRESSED
            if not active_buttons:
                stop_all_motors()
                continue

            # CHECK FOR ROTATION FIRST
            if event.code == evdev.ecodes.BTN_SOUTH and event.value == 1:  # X button (Rotate Left)
                print("Rotating Left")
                stop_all_motors()  
                rotate_left(speed)
                continue
            elif event.code == evdev.ecodes.BTN_EAST and event.value == 1:  # O button (Rotate Right)
                print("Rotating Right")
                stop_all_motors()  
                rotate_right(speed)
                continue

            # CHECK FOR DIAGONAL MOVEMENT
            x = button_states.get("ABS_HAT0X", 0)
            y = button_states.get("ABS_HAT0Y", 0)

            if x != 0 and y != 0:  # Both directions pressed -> move diagonally
                stop_all_motors()  
                
                if y == -1 and x == -1:
                    print("move_diagonal_front_left")
                    move_diagonal_front_left(speed)
                elif y == -1 and x == 1:
                    print("move_diagonal_front_right")
                    move_diagonal_front_right(speed)
                elif y == 1 and x == -1:
                    print("move_diagonal_back_left")
                    move_diagonal_back_left(speed)
                elif y == 1 and x == 1:
                    print("move_diagonal_back_right")
                    move_diagonal_back_right(speed)

                continue  

            # SINGLE BUTTON ACTIONS (ONLY RUN IF NO DIAGONAL OR ROTATION DETECTED)
            stop_all_motors()  
            
            if event.code == evdev.ecodes.BTN_TL and event.value:  # L1 increases speed
                speed = min(speed + 10, MAX_SPEED)
                print(f"[INFO] Speed increased: {speed}%")
            if event.code == evdev.ecodes.BTN_TR and event.value:  # R1 increases speed
                speed = min(speed + 10, MAX_SPEED)
                print(f"[INFO] Speed increased: {speed}%")

            if event.code == evdev.ecodes.BTN_TL2 and event.value:  # L2 decreases speed
                speed = max(speed - 10, MIN_SPEED)
                print(f"[INFO] Speed decreased: {speed}%")
            if event.code == evdev.ecodes.BTN_TR2 and event.value:  # R2 decreases speed
                speed = max(speed - 10, MIN_SPEED)
                print(f"[INFO] Speed decreased: {speed}%")
                
            
            if event.code == evdev.ecodes.ABS_HAT0Y:
                if event.value == -1:
                    move_forward(speed)
                elif event.value == 1:
                    move_backward(speed)
                else:
                    stop_all_motors()
            elif event.code == evdev.ecodes.ABS_HAT0X:
                if event.value == -1:
                    strafe_left(speed)
                elif event.value == 1:
                    strafe_right(speed)
                else:
                    stop_all_motors()

except KeyboardInterrupt:
    print("\n[INFO] Program terminated.")

finally:
    stop_all_motors()
    print("[INFO] Robot stopped.")


