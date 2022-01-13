from logging import getLogger

logger = getLogger(__name__)

from hal import led, buzzer, radiator
import hal

from scheduler import DateTimeMatch, Scheduler

scheduler = Scheduler("radiator", radiator.on, radiator.off, persist=True)

import uasyncio as asyncio

# say hello to the world
for _ in range(3):
    asyncio.run(led.flash(led.RED, 0.2))
    asyncio.run(led.flash(led.GREEN, 0.2))
logger.info("Everything started")

loop = asyncio.get_event_loop()
hal.init(loop)

loop.run_forever()
