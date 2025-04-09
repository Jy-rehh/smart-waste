import smbus
from time import sleep

# I2C address for the LCD
I2C_ADDR = 0x27  # Adjust this address if necessary (some displays use 0x3F)
bus = smbus.SMBus(1)  # For Raspberry Pi models with I2C bus 1

# LCD configuration
LCD_WIDTH = 20  # 20 characters per line
LCD_CMD = 0x00   # Command mode
LCD_CHR = 0x01   # Character mode

# Commands
LCD_LINE_1 = 0x80  # Address for the first line
LCD_LINE_2 = 0xC0  # Address for the second line
LCD_LINE_3 = 0x94  # Address for the third line (20x4 display)
LCD_LINE_4 = 0xD4  # Address for the fourth line (20x4 display)

# Initialize the LCD
def lcd_init():
    sleep(0.5)
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    sleep(0.5)

# Send a byte to the LCD
def lcd_byte(bits, mode):
    bus.write_byte(I2C_ADDR, mode)
    bus.write_byte(I2C_ADDR, bits)
    bus.write_byte(I2C_ADDR, bits << 4)

# Write a string to the LCD
def lcd_string(message, line):
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        if i < len(message):
            lcd_byte(ord(message[i]), LCD_CHR)
        else:
            lcd_byte(0x20, LCD_CHR)

# Display a message
def display_message(message):
    lcd_string(message, LCD_LINE_1)  # Display message on the first line

# Test the LCD
lcd_init()
display_message("Hello, World!")
sleep(2)
display_message("20x4 LCD Test")
sleep(2)
