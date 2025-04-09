import smbus
from time import sleep

# LCD setup (assuming you are using I2C)
I2C_ADDR = 0x27
bus = smbus.SMBus(1)
LCD_WIDTH = 16

LCD_CMD = 0x00  # Command mode
LCD_CHR = 0x01  # Character mode

def lcd_byte(bits, mode):
    bus.write_byte(I2C_ADDR, mode)
    bus.write_byte(I2C_ADDR, bits)
    bus.write_byte(I2C_ADDR, bits << 4)

def lcd_string(message, line):
    lcd_byte(0x80 | line, LCD_CMD)  # Move to the correct line
    for i in range(LCD_WIDTH):
        if i < len(message):
            lcd_byte(ord(message[i]), LCD_CHR)
        else:
            lcd_byte(0x20, LCD_CHR)  # Empty space for unused part of the line

def display_message(message):
    print(f"Displaying message: {message}")
    lcd_string(message, 0)  # Display on the first line
    sleep(2)  # Show the message for 2 seconds

print("Testing LCD display...")
display_message("Hello, World!")
print("LCD test complete.")
