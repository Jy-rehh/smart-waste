import RPi.GPIO as GPIO
import time

TRIG_PIN = 11
ECHO_PIN = 8

GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

container_full = False  # Shared flag

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
