import smbus
from time import sleep

# I2C address for the LCD (change to 0x3F if needed)
I2C_ADDR = 0x27
bus = smbus.SMBus(1)

# LCD configuration
LCD_WIDTH = 20
LCD_CMD = 0x00
LCD_CHR = 0x01

# Line addresses for a 20x4 LCD
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_LINE_3 = 0x94
LCD_LINE_4 = 0xD4

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
    try:
        bus.write_byte(I2C_ADDR, mode)
        bus.write_byte(I2C_ADDR, bits)
        bus.write_byte(I2C_ADDR, bits << 4)
    except Exception as e:
        print(f"LCD write error: {e}")

# Write a message to a specific line
def lcd_string(message, line):
    lcd_byte(line, LCD_CMD)
    message = message.ljust(LCD_WIDTH, " ")[:LCD_WIDTH]
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

# Shortcut to show one message across 4 lines (optional)
def display_lines(line1="", line2="", line3="", line4=""):
    lcd_string(line1, LCD_LINE_1)
    lcd_string(line2, LCD_LINE_2)
    lcd_string(line3, LCD_LINE_3)
    lcd_string(line4, LCD_LINE_4)

# Test when run directly
if __name__ == "__main__":
    lcd_init()
    display_lines("Line 1: Hello", "Line 2: World", "Line 3: 20x4 LCD", "Line 4: Working!")
    sleep(5)
    display_lines("Ready for", "Plastic Bottle", "Detection!", "")
