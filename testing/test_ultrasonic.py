import RPi.GPIO as GPIO
import time

# Set the pin numbering mode to GPIO.BOARD for physical pin numbers
GPIO.setmode(GPIO.BOARD)

# Cleanup GPIO to avoid warnings about pins being already in use
GPIO.cleanup()

# Set physical pin numbers
TRIG_PIN = 26  # Physical pin 26
ECHO_PIN = 24  # Physical pin 24

# Setup pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# --- Shared flag for fullness ---
container_full = False

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
            return None

    timeout = time.time() + 0.04
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def monitor_container():
    global container_full
    try:
        while True:
            distance = get_distance()
            if distance is not None:
                print(f"[Ultrasonic] Distance: {distance} cm")
                container_full = distance <= 4
            else:
                print("[Ultrasonic] Sensor error.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Ultrasonic] Monitoring stopped.")
    finally:
        GPIO.cleanup()
