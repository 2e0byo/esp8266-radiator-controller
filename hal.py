from math import pi, sin

import uasyncio as asyncio
from machine import PWM, Pin

relay = Pin(0, Pin.OUT)
relay.off()


led1 = Pin(16, Pin.OUT)
led2 = Pin(5, Pin.OUT)
led = PWM(led2)

duties = {"red": 0, "green": 0}
colour = "red"


def led_colour(col: str):
    global led, led1, colour, duties
    if col == "green":
        led1.off()
        led.duty(duties[col])
        colour = "green"
    elif col == "red":
        led1.on()
        led.duty(1023 - duties[col])
        colour = "red"


led_colour("red")


def led_brightness(br):
    if colour == "red":
        led.duty(1023 - br)
    else:
        led.duty(br)
    duties["colour"] = br


async def flash(colour, duration):
    led_colour(colour)
    for step in range(100):
        led_brightness(round(sin(pi * step / 100) * 1023))
        await asyncio.sleep(duration / 100)

    led_brightness(0)
