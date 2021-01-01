import uasyncio as asyncio
from machine import PWM, Pin

buzzer = PWM(Pin(12))
buzzer.duty(0)

sound = True


async def siren():
    buzzer.duty(512)
    while sound:
        buzzer.freq(440)
        await asyncio.sleep(0.5)
        buzzer.freq(600)
        await asyncio.sleep(0.5)
    buzzer.duty(0)


def ring():
    buzzer.freq(600)
    while sound:
        for i in range(2):
            buzzer.duty(512)
            await asyncio.sleep(0.1)
            buzzer.duty(0)
            await asyncio.sleep(0.1)
        await asyncio.sleep(0.4)

    buzzer.duty(0)
