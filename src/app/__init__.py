import gc
from logging import getLogger

import uasyncio as asyncio

from . import wdt


def _step():
    wdt.feed()
    gc.collect()


logger = getLogger(__name__)
logger.debug("App booting...")

logger.debug("Importing hal")
from . import hal

_step()

logger.debug("Importing radiator")
from . import radiator

_step()

logger.debug("Importing api")
from . import api

_step()


def blink_hello():
    # say hello to the world
    for _ in range(3):
        asyncio.run(hal.led.flash(hal.led.RED, 0.2))
        asyncio.run(hal.led.flash(hal.led.GREEN, 0.2))


blink_hello()
logger.info("Everything started")
print(f"WDT validating the state of {len(wdt.state) - 1} processes.")

loop = asyncio.get_event_loop()
loop.run_forever()
