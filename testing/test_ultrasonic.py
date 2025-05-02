import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import datetime
import RPi.GPIO as GPIO

# Set up GPIO for the first ultrasonic sensor
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG1 = 11  # GPIO Pin 11 (changed)
ECHO1 = 8   # GPIO Pin 8 (changed)

GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)

def get_distance(TRIG, ECHO):
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()

    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def send_email(timestamp):
    sender_email = "smartaccesssmartwaste@gmail.com"
    receiver_email = "smartaccesssmartwaste@gmail.com"
    password = "ospk xejd cpxz djbh"

    subject = "📦 RVM Notification: Bottle Bin Full – Collection Required"
    body = f"""
    Hello,

    This is an automated notification from the RVM Smart Waste Smart Access System.

    The bottle bin has reached full capacity as of {timestamp}. Bottles are now ready for collection.

    Timestamp: {timestamp}

    To ensure continued service and prevent overflow, please schedule a pickup at your earliest convenience.

    Thank you for your attention.

    —
    RVM System Notification
    This is a system-generated email. Please do not reply.
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"[{timestamp}] Email sent successfully!")
    except Exception as e:
        print(f"[{timestamp}] Failed to send email: {e}")

try:
    while True:
        last_email_time = 0  # Timestamp of last sent email
        EMAIL_COOLDOWN = 3600  # 1 hour in seconds

        distance1 = get_distance(TRIG1, ECHO1)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Sensor 1 Distance: {distance1} cm")

        if distance1 < 6:
            current_time = time.time()
            if current_time - last_email_time >= EMAIL_COOLDOWN:
                print(f"[{timestamp}] Container Full!")
                send_email(timestamp)
                last_email_time = current_time
            else:
                print(f"[{timestamp}] Bin full, email already sent.")

        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped.")
    GPIO.cleanup()
