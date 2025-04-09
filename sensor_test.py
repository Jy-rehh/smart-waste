from gpiozero import Servo
from time import sleep
import smbus
import time

# Initialize the servo
servo = Servo(17)  # You can change to any GPIO pin supporting PWM

# Initialize the I2C bus and LCD (using smbus for I2C communication)
bus = smbus.SMBus(1)
LCD_ADDR = 0x27  # Default I2C address for most LCDs, check if it's different

# Function to send a command to the LCD
def lcd_command(command):
    bus.write_byte(LCD_ADDR, command)
    time.sleep(0.001)

# Function to write data to the LCD
def lcd_write(message):
    for char in message:
        bus.write_byte(LCD_ADDR, ord(char))
        time.sleep(0.001)

# Function to clear the display
def lcd_clear():
    lcd_command(0x01)  # Clear the display
    time.sleep(0.001)

# Test LCD
lcd_clear()
lcd_command(0x80)  # Move cursor to beginning of the first line
lcd_write("24x4 LCD Test")  # Display message on first line

# Test Servo
servo.value = 1  # Move servo to the right
sleep(1)
servo.value = -1  # Move servo to the left
sleep(1)
servo.value = 0  # Center the servo
sleep(1)
