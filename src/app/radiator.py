import uasyncio as asyncio
from machine import Pin
from primitives.pushbutton import Pushbutton
from settings import settings

from .hal import radiator, buzzer, led
from .scheduler import DateTimeMatch, Scheduler

scheduler = Scheduler("radiator", radiator.on, radiator.off, persist=True)
scheduler.append(DateTimeMatch(hour=8), 60)
scheduler.append(DateTimeMatch(hour=22, minute=30), 60)


button = Pushbutton(Pin(2, Pin.IN), suppress=True)


def toggle(state=[]):
    if state:
        scheduler.pop_once()
        state.pop()
        asyncio.create_task(buzzer.beep(duration_ms=50))
    else:
        scheduler.append_once(settings.get("radiator-on-time", 45))
        state.append(0)
        asyncio.create_task(buzzer.beep(duration_ms=50))


button.press_func(toggle)
