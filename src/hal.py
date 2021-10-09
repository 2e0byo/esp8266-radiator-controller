import uasyncio as asyncio
from primitives.delay_ms import Delay_ms
from primitives.message import Message

from math import pi, sin
from machine import PWM, Pin


class Radiator:
    HEATING_ON = 0
    HEATING_OFF = 1
    WARMING_ON = 2
    WARMING_OFF = 3

    def __init__(self, relay):
        self._relay = relay
        relay.off()
        self._warm_ms = 30 * 60 * 1000
        self._timer = Delay_ms(self._warm_off, self.delay)
        self._timer.stop()
        self._warming = False
        self._heating = False
        self._update = Message()

    def start(self, loop):
        loop.create_task(self._loop())

    @property
    def delay(self):
        return self._warm_ms / 60_000

    @delay.setter
    def delay(self, val):
        self._warm_ms = delay * 60_000
        self._timer._durn = self._warm_ms

    @property
    def heating(self):
        return self._heating

    @heating.setter
    def heating(self, val):
        if self._heating is not val:
            self._heating = val
            state = self.HEATING_ON if val else self.HEATING_OFF
            self._update.set(state)

    @property
    def warming(self):
        return self._warming

    @warming.setter
    def warming(self, val):
        if self._warming is not val:
            self._warming = val
            if val:
                state = self.WARMING_ON
                self._timer.trigger()
            else:
                state = self.WARMING_OFF
                self._timer.stop()
            self._update.set(state)

    def stop_warm(self):
        self._update.set(self.WARMING_OFF)

    async def _loop(self):
        while True:
            msg = await self._update.wait()
            if msg is self.HEATING_ON:
                self.relay.on()
            elif msg is self.HEATING_OFF and not self._warming:
                self.relay.off()
            elif msg is self.WARMING_ON:
                self.relay.on()
            elif msg is self.WARMING_OFF and not self._heating:
                self.relay_off()


class LED:
    # led which can be flashed nicely
    RED = 0
    GREEN = 1

    def __init__(self, led, other_pin):
        self.other_pin = other_pin
        self.led = led
        self.set_colour(self.GREEN)
        self.set_brightness(0)

    def set_colour(self, col):
        if col is self.GREEN:
            self.other_pin.off()
        else:
            self.other_pin.on()

    def set_brightness(self, duty):
        if col is self.GREEN:
            self.led.duty(duty)
        else:
            self.led.duty(1023 - duty)

    async def flash(self, colour, duration):
        gap = duration / 100
        self.set_colour(colour)
        for step in range(100):
            self.set_brightness(round(sin(pi * step / 100) * 1023))
            await asyncio.sleep(gap)
        self.set_brightness(0)


def init(loop):
    _relay = Pin(0, Pin.OUT)
    radiator = Radiator(_relay)
    radiator.start(loop)

    _led1 = Pin(16, Pin.OUT)
    _led2 = Pin(5, Pin.OUT)
    _pwm = PWM(led2)
    led = LED(_pwm, _led1)
