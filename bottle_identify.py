# bottle_identify.py

import threading
import time
import RPi.GPIO as GPIO

TRIG_PIN = 11
ECHO_PIN = 8

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

distance = None  # Shared global

def ultrasonic_loop():
    global distance
    while True:
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.05)

        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        timeout = time.time() + 0.04
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
            if time.time() > timeout:
                distance = None
                break

        timeout = time.time() + 0.04
        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
            if time.time() > timeout:
                distance = None
                break

        try:
            pulse_duration = pulse_end - pulse_start
            distance = round(pulse_duration * 17150, 2)
        except:
            distance = None

        time.sleep(1)

def start_ultrasonic_thread():
    thread = threading.Thread(target=ultrasonic_loop, daemon=True)
    thread.start()

def get_distance():
    return distance
