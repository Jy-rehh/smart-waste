from gpiozero import Servo
from time import sleep
import smbus
import time

# Initialize the servo
servo = Servo(17)  # You can change to any GPIO pin supporting PWM

# Initialize the I2C bus and LCD (using smbus for I2C communication)
bus = smbus.SMBus(1)
LCD_ADDR = 0x27  # Default I2C address for most LCDs, confirmed as detected

# LCD Command Functions
def lcd_command(command):
    bus.write_byte(LCD_ADDR, command)
    time.sleep(0.001)

def lcd_write(message):
    for char in message:
        bus.write_byte(LCD_ADDR, ord(char))
        time.sleep(0.001)

def lcd_clear():
    lcd_command(0x01)  # Clear the display
    time.sleep(0.001)

# LCD Initialization
def lcd_init():
    lcd_command(0x38)  # Function set: 8-bit, 2-line, 5x8 dots
    lcd_command(0x0C)  # Display on, cursor off
    lcd_command(0x06)  # Entry mode: Increment cursor
    lcd_command(0x01)  # Clear display

# Test LCD
lcd_init()
lcd_clear()
lcd_command(0x80)  # Move cursor to the beginning of the first line
lcd_write("24x4 LCD Test")  # Display message on first line

# Test Servo
servo.value = 1  # Move servo to the right
sleep(1)
servo.value = -1  # Move servo to the left
sleep(1)
servo.value = 0  # Center the servo
sleep(1)
