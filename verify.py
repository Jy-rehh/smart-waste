# import RPi.GPIO as GPIO
# import time

# # --- Pin Definitions ---
# TRIG_PIN = 10  # Physical pin 19
# ECHO_PIN = 9   # Physical pin 21

# # --- Setup ---
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(TRIG_PIN, GPIO.OUT)
# GPIO.setup(ECHO_PIN, GPIO.IN)

# def get_distance():
#     GPIO.output(TRIG_PIN, False)
#     time.sleep(0.05)

#     # Trigger pulse
#     GPIO.output(TRIG_PIN, True)
#     time.sleep(0.00001)  # 10µs pulse
#     GPIO.output(TRIG_PIN, False)

#     # Wait for echo to start
#     timeout = time.time() + 0.04
#     while GPIO.input(ECHO_PIN) == 0:
#         pulse_start = time.time()
#         if time.time() > timeout:
#             print("Timeout waiting for echo to start")
#             return None

#     # Wait for echo to end
#     timeout = time.time() + 0.04
#     while GPIO.input(ECHO_PIN) == 1:
#         pulse_end = time.time()
#         if time.time() > timeout:
#             print("Timeout waiting for echo to end")
#             return None

#     pulse_duration = pulse_end - pulse_start
#     distance = pulse_duration * 17150  # Speed of sound / 2

#     return round(distance, 2)

# try:
#     print("Ultrasonic sensor ready. Press Ctrl+C to stop.")
#     while True:
#         dist = get_distance()
#         if dist is not None:
#             print(f"Distance: {dist} cm")
#         else:
#             print("Sensor error or out of range.")
#         time.sleep(0.5)

# except KeyboardInterrupt:
#     print("\nMeasurement stopped by user.")

# finally:
#     GPIO.cleanup()
# verify.py
# verify.py
import RPi.GPIO as GPIO
import time

TRIG_PIN = 10  # BCM pin
ECHO_PIN = 9   # BCM pin

def setup_ultrasonic():
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.05)

    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    timeout = time.time() + 0.04
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            print("Timeout waiting for echo to start")
            return None

    timeout = time.time() + 0.04
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            print("Timeout waiting for echo to end")
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)
