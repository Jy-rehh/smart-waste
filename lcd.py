import smbus
from time import sleep

I2C_ADDR = 0x27  # Adjust if your address is different
LCD_WIDTH = 24    # For 24x4 LCD

LCD_CMD = 0x00  # Command mode
LCD_CHR = 0x01  # Character mode

bus = smbus.SMBus(1)

def lcd_byte(bits, mode):
    """Send a byte to the LCD in the specified mode."""
    bus.write_byte(I2C_ADDR, mode)
    bus.write_byte(I2C_ADDR, bits)
    bus.write_byte(I2C_ADDR, bits << 4)

def lcd_string(message, line):
    """Display a string message on the specified LCD line."""
    lcd_byte(0x80 | line, LCD_CMD)  # Position the cursor
    for i in range(LCD_WIDTH):
        if i < len(message):
            lcd_byte(ord(message[i]), LCD_CHR)
        else:
            lcd_byte(0x20, LCD_CHR)  # Pad with spaces

def display_message(message):
    """Display the message on the first line of the LCD."""
    lcd_string(message, 0)  # Display on first line
    sleep(2)

# Example usage:
display_message("Hello, World!")
