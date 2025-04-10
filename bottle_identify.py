import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    # Trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10µs pulse
    GPIO.output(TRIG, False)

    # Wait for echo start
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Wait for echo end
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate distance (speed of sound = 34300 cm/s)
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # cm
    return round(distance, 2)

try:
    while True:
        dist = measure_distance()
        print(f"Bottle Distance: {dist} cm")
        if dist < 10:
            print("✅ Bottle Detected!")
        else:
            print("⚠️ No Bottle")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
