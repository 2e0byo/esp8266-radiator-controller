import uasyncio as asyncio
from primitives.delay_ms import Delay_ms
from primitives.message import Message

from math import pi, sin
from machine import PWM, Pin


class Led:
    # led which can be flashed nicely
    RED = 0
    GREEN = 1
    FADE_STEPS = bytearray(round(sin(pi * x / 100) * 255) for x in range(100))

    def __init__(self, led, other_pin):
        self.other_pin = other_pin
        self.led = led
        self._brightness = 0
        self.set_colour(self.GREEN)

    def set_colour(self, col):
        self._colour = col
        if col is self.GREEN:
            self.other_pin.off()
        else:
            self.other_pin.on()
        self.set_brightness(self._brightness)

    def set_brightness(self, duty):
        self._brightness = duty
        if self._colour is self.GREEN:
            self.led.duty(duty)
        else:
            self.led.duty(1023 - duty)

    async def flash(self, colour=None, duration=1):
        gap = duration / 100
        if colour is not None:
            self.set_colour(colour)
        for step in range(100):
            self.set_brightness(self.FADE_STEPS[step] * 4)
            await asyncio.sleep(gap)
        self.set_brightness(0)


class Buzzer:
    SOUND_OFF = 0
    SOUND = 1
    RING = 2
    RING_OFF = 3

    def __init__(self, buzzer):
        self._buzzer = buzzer
        self._buzzer.duty(0)
        self._sounding = False
        self._ringing = False
        self._update = Message()
        self.ring_freq = 600
        asyncio.create_task(self._loop())

    def start(self, loop):
        loop.create_task(self._loop())

    @property
    def sounding(self):
        return self._sounding

    @sounding.setter
    def sounding(self, val):
        if val and not self._sounding:
            self._update.set(self.SOUND)
        elif not val and self._sounding:
            self._update.set(self.SOUND_OFF)

    @property
    def ringing(self):
        return self._ringing

    @ringing.setter
    def ringing(self, val):
        if val and not self._ringing:
            self._update.set(self.RING)
        elif not val and self._ringing:
            self._update.set(self.RING_OFF)

    async def _siren(self):
        self._buzzer.duty(512)
        while self._sounding:
            self._buzzer.freq(440)
            await asyncio.sleep(0.5)
            self._buzzer.freq(600)
            await asyncio.sleep(0.5)
        self._buzzer.duty(0)

    async def _ring(self):
        while self._ringing:
            for _ in range(2):
                self._buzzer.freq(self.ring_freq)
                self._buzzer.duty(512)
                await asyncio.sleep(0.1)
                self._buzzer.duty(0)
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.4)
        self._buzzer.duty(0)

    async def beep(self, freq=600, duration_ms=500):
        self._buzzer.duty(0)
        self._buzzer.freq(freq)
        self._buzzer.duty(512)
        await asyncio.sleep_ms(duration_ms)
        self._buzzer.duty(0)

    def _loop(self):
        while True:
            msg = await self._update.wait()
            if msg is self.SOUND and not self._sounding:
                self._sounding = True
                asyncio.get_event_loop().create_task(self._siren())
            elif msg is self.SOUND_OFF and self._sounding:
                self._sounding = False
            elif msg is self.RING and not self._ringing:
                self._ringing = True
                asyncio.get_event_loop().create_task(self._ring())
            elif msg is self.RING_OFF and self._ringing:
                self._ringing = False


class NoisyPin(Pin):
    def __init__(self, *args, led, **kwargs):
        super().__init__(*args)
        self._led = led

    async def _flash(self, colour):
        for _ in range(3):
            await self._led.flash(colour, 0.1)
            await asyncio.sleep(0.1)

        await self._led.flash(colour, 0.3)

    def on(self):
        asyncio.create_task(self._flash(self._led.GREEN))
        super().on()

    def off(self):
        asyncio.create_task(self._flash(self._led.RED))
        super().off()


_led1 = Pin(16, Pin.OUT)
_led2 = Pin(5, Pin.OUT)

_pwm = PWM(_led2)
led = Led(_pwm, _led1)
radiator = NoisyPin(0, Pin.OUT, led=led)

_buzzer = PWM(Pin(12))
buzzer = Buzzer(_buzzer)
