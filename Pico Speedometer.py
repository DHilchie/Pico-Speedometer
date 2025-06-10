from machine import Pin, ADC, I2C
from time import sleep, ticks_ms
from i2c_lcd import I2cLcd

# Setup I2C LCD
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

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

lcd.backlight_on()
lcd.clear()
lcd.putstr("SPEEDOMETER\nReady for HO")

def analog_read(sensor):
    return sensor.read_u16() >> 4  # scale to ~0–4095

while True:
    value1 = analog_read(sensor1)
    value2 = analog_read(sensor2)
    now = ticks_ms()
    idle_time = now - idlemillis1

    if idle_time > 180000:  # 3 minutes
        lcd.backlight_off()

    if count_state == 'OFF':
        if value1 < 500:
            startmillis = ticks_ms()
            count_state = 'RIGHT'
        elif value2 < 500:
            startmillis = ticks_ms()
            count_state = 'LEFT'

    elif count_state == 'LEFT':
        lcd.backlight_on()
        if value1 < 500:
            endmillis = ticks_ms()
            count_state = 'DONE'
        status_led.value(1)
        lcd.move_to(15, 1)
        lcd.putchar('L')

    elif count_state == 'RIGHT':
        lcd.backlight_on()
        if value2 < 500:
            endmillis = ticks_ms()
            count_state = 'DONE'
        status_led.value(1)
        lcd.move_to(15, 1)
        lcd.putchar('R')

    elif count_state == 'DONE':
        time_ms = endmillis - startmillis
        sec1 = time_ms / 1000.0
        feet1 = dist1 / 12.0
        rate1 = feet1 / sec1
        scale1 = int(rate1 * 59.31 + 0.5)

        lcd.backlight_on()
        lcd.clear()
        lcd.putstr(f"Speed: {scale1} mph\nLast:  {scale2} mph")

        scale2 = scale1
        status_led.value(0)
        sleep(5)
        count_state = 'RESET'

    elif count_state == 'RESET':
        lcd.clear()
        lcd.putstr("RESETTING")
        sleep(0.5)
        lcd.clear()
        lcd.putstr("SPEEDOMETER\nReady for HO")
        count_state = 'OFF'
        idlemillis1 = ticks_ms()
