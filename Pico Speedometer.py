from machine import Pin, ADC, I2C
from time import sleep, ticks_ms
import ssd1306

# Setup I2C OLED
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Setup pins
sensor1 = ADC(Pin(26))  # GP26 = ADC0
sensor2 = ADC(Pin(27))  # GP27 = ADC1
status_led = Pin(15, Pin.OUT)

# Variables
dist1 = 2.25  # inches between sensors
scale2 = 0
count_state = 'OFF'
startmillis = 0
endmillis = 0
idlemillis1 = ticks_ms()

def analog_read(sensor):
    return sensor.read_u16() >> 4  # ~0–4095

def display_text(line1, line2="", line3="", line4=""):
    oled.fill(0)
    oled.text(line1, 0, 0)
    oled.text(line2, 0, 16)
    oled.text(line3, 0, 32)
    oled.text(line4, 0, 48)
    oled.show()

# Initial display
display_text("SPEEDOMETER", "Ready for HO")

while True:
    value1 = analog_read(sensor1)
    value2 = analog_read(sensor2)
    now = ticks_ms()
    idle_time = now - idlemillis1

    if idle_time > 180000:
        oled.poweroff()  # Turn off OLED to save power

    if count_state == 'OFF':
        if value1 < 500:
            startmillis = ticks_ms()
            count_state = 'RIGHT'
        elif value2 < 500:
            startmillis = ticks_ms()
            count_state = 'LEFT'

    elif count_state == 'LEFT':
        oled.poweron()
        if value1 < 500:
            endmillis = ticks_ms()
            count_state = 'DONE'
        status_led.value(1)
        display_text("Counting...", "Direction: L")

    elif count_state == 'RIGHT':
        oled.poweron()
        if value2 < 500:
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
