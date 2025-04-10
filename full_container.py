import RPi.GPIO as GPIO
import time

TRIG = 27
ECHO = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

try:
    while True:
        dist = measure_distance()
        print(f"Container Level: {dist} cm")
        if dist < 5:
            print("🟥 Container is FULL!")
        else:
            print("🟩 Container has space.")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
