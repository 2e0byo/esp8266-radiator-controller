from logging import getLogger

logger = getLogger(__name__)

from hal import led, buzzer, radiator
import hal

from scheduler import DateTimeMatch, Scheduler

scheduler = Scheduler("radiator", radiator.on, radiator.off, persist=True)
scheduler.append(DateTimeMatch(hour=8), 60)
scheduler.append(DateTimeMatch(hour=22, minute=30), 60)

from primitives.pushbutton import Pushbutton
from machine import Pin
from settings import settings

button = Pushbutton(Pin(2, Pin.IN), suppress=True)


def toggle(state=[]):
    if state:
        scheduler.pop_once()
        state.pop()
        asyncio.create_task(led.flash(led.RED))
    else:
        scheduler.append_once(settings.get("radiator-on-time", 45))
        state.append(0)
        asyncio.create_task(led.flash(led.GREEN))


button.press_func(toggle)

import uasyncio as asyncio

# say hello to the world
for _ in range(3):
    asyncio.run(led.flash(led.RED, 0.2))
    asyncio.run(led.flash(led.GREEN, 0.2))
logger.info("Everything started")

loop = asyncio.get_event_loop()
hal.init(loop)

loop.run_forever()
