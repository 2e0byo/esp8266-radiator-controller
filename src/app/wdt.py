import uasyncio as asyncio
from machine import WDT

state = {"wdt": True}
_wdt = WDT()


def feed():
    from time import time

    """Manually feed the wdt."""
    # print("feeding wdt", time())
    _wdt.feed()


async def heartbeat():
    """
    Restart the machine if the asyncio loop locks up, or a task signals to do so.

    Tasks can add a key/value pair to the dict `wdt.state`; setting the value
    to anything falsy will cause the WDT to throw.  This method depends upon
    the task not dying before signalling and is thus inherently weak, but easy
    to implement.  Critical tasks should consider this and structure their
    exception handlers accordingly.
    """
    while True:
        if all(state.values()):
            feed()
            await asyncio.sleep(1)
        else:
            raise Exception("Not all state is as it should be!")


loop = asyncio.get_event_loop()
loop.create_task(heartbeat())
