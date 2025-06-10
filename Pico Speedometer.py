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
status_led = Pin(15, Pin.OUT)

# --- Variables ---
dist1 = 2.25  # inches between IR sensors
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
