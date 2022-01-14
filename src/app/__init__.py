import uasyncio as asyncio
from logging import getLogger

logger = getLogger(__name__)
logger.debug("App booting...")

logger.debug("Importing hal")
from . import hal

logger.debug("Importing radiator")
from . import radiator

logger.debug("Importing api")
from . import api


def blink_hello():
    # say hello to the world
    for _ in range(3):
        asyncio.run(hal.led.flash(hal.led.RED, 0.2))
        asyncio.run(hal.led.flash(hal.led.GREEN, 0.2))


blink_hello()
logger.info("Everything started")


async def heartbeat():
    while True:
        print("beep-beep")
        await asyncio.sleep(5)


loop = asyncio.get_event_loop()
loop.run_forever()
