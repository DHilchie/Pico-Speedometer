#  Speedometer program adapted by John Crellin May 2025
#  This version was modified for a 4 line display
#  original program written by DIY and Digital Railroad 
#  https://youtu.be/Z_OI1jTq_2A?si=aiDp-qr3_nx_WhXf
#  This version allows for the loco to start either left or right side
#  It also converts to scale MPH for HO
#  Can be adapted for other scales or to KPH by changing the scale rate
#
#  Once you have installed the sensors variable dist1 must be changed to the decimal distance in inches
#  between the installed sensors
#  example 2.25 is 2 and 1/4 inches distance between sensors
#
#  Make sure the LCD_I2C library has been downloaded to your arduino IDE
#
#  You can choose to attach an LED with resistor to pin 12
#  this LED will go HIGH when the first sensor is triggered
#  then it will go back LOW when the speedometer resets
#
#  The display is a standard 2x16 LCD display with I2C board attached
#  On the display connect SCL to A5 and SDA to A4
#  
#  If you wish to use Photocells.  I have found the best version(s) to use without changing the code 
#  are the 5528 and 5537 photocells
#
#  code added to add the last reading to the display - May 2025
#  code added to turn off the backlight if idle for 3 minutes. Any trigger turns it back on. - June 2025
#
#  CHAT GPT converted code to run on Pi Pico using Micro Python, OLED display, and IR sensors. - 2025.06.09

from machine import Pin, I2C
from time import sleep, ticks_ms
import ssd1306

# Define I2C pins and OLED display address
I2C_SCL_PIN = 9
I2C_SDA_PIN = 8
I2C_FREQ = 400000
OLED_ADDR = 0x3d

# Initialize I2C object and OLED display object
i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=OLED_ADDR)

# --- IR Sensors (digital input) ---
sensor1 = Pin(10, Pin.IN, Pin.PULL_UP)  # IR sensor 1
sensor2 = Pin(11, Pin.IN, Pin.PULL_UP)  # IR sensor 2

# --- Status LED ---
status_led = Pin(14, Pin.OUT)

# --- Variables ---
dist1 = 2.50  # inches between IR sensors
scale2 = 0
count_state = 'OFF'
startmillis = 0
endmillis = 0
idlemillis1 = ticks_ms()

# --- Helper to draw 4 lines ---
def display_text(line1="", line2="", line3="", line4=""):
    oled.fill(0)
    if line1: oled.text(line1, 0, 0)
    if line2: oled.text(line2, 0, 16)
    if line3: oled.text(line3, 0, 32)
    if line4: oled.text(line4, 0, 48)
    oled.show()

# --- Initial Screen ---
display_text("SPEEDOMETER", "Ready for HO")

# --- Main Loop ---
while True:
    val1 = sensor1.value()
    val2 = sensor2.value()
    now = ticks_ms()
    idle_time = now - idlemillis1

    if idle_time > 180000:
        oled.poweroff()

    if count_state == 'OFF':
        if val1 == 0:  # sensor 1 triggered
            startmillis = ticks_ms()
            count_state = 'RIGHT'
        elif val2 == 0:  # sensor 2 triggered
            startmillis = ticks_ms()
            count_state = 'LEFT'

    elif count_state == 'LEFT':
        oled.poweron()
        if val1 == 0:
            endmillis = ticks_ms()
            count_state = 'DONE'
        status_led.value(1)
        display_text("Counting...", "Direction: L")

    elif count_state == 'RIGHT':
        oled.poweron()
        if val2 == 0:
            endmillis = ticks_ms()
            count_state = 'DONE'
        status_led.value(1)
        display_text("Counting...", "Direction: R")

    elif count_state == 'DONE':
        time_ms = endmillis - startmillis
        sec1 = time_ms / 1000.0
        feet1 = dist1 / 12.0
        rate1 = feet1 / sec1
        scale1 = int(rate1 * 59.31 + 0.5)

        display_text(
            f"Speed: {scale1} mph",
            f"Last:  {scale2} mph"
        )

        scale2 = scale1
        status_led.value(0)
        sleep(5)
        count_state = 'RESET'

    elif count_state == 'RESET':
        display_text("RESETTING...")
        sleep(0.5)
        display_text("SPEEDOMETER", "Ready for HO")
        count_state = 'OFF'
        idlemillis1 = ticks_ms()
