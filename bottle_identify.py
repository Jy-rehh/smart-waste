import RPi.GPIO as GPIO
import time

# Pin Definitions
TRIG_PIN = 23  # You can change these to your wiring
ECHO_PIN = 24

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    # Ensure trigger is low
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.05)

    # Send 10µs pulse
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  # 10 microseconds
    GPIO.output(TRIG_PIN, False)

    # Wait for echo to start
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    # Wait for echo to end
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # Duration of echo pulse
    pulse_duration = pulse_end - pulse_start

    # Distance in cm
    distance = pulse_duration * 17150  # speed of sound: 34300 cm/s ÷ 2

    return round(distance, 2)

try:
    while True:
        dist = get_distance()
        print(f"Distance: {dist} cm")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()
