# from RPLCD.i2c import CharLCD
# from time import sleep

# lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4, dotsize=8)
# lcd.clear()

# lcd.write_string("Line 1: Hello")
# lcd.crlf()
# lcd.write_string("Line 2: World")
# sleep(2)
# lcd.clear()
# lcd.write_string("Ready for bottle!")

# lcd.py
from RPLCD.i2c import CharLCD
from time import sleep

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4, dotsize=8)

def display_message(message):
    lcd.clear()
    lcd.write_string(message)
