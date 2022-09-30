import json
from collections import namedtuple

import uasyncio as asyncio
from packing.packed import PackedRotatingLog
from settings import settings

from .radiator import radiator as radiator_hardware
from .radiator import scheduler
from .temperature import sensor

packer = PackedRotatingLog(
    "temperature",
    "/static/",
    log_lines=settings.get("temperature-log-size", 1440),
    floats=1,
    ints=0,
    bools=1,
    keep_logs=settings.get("keep-temperature-logs", 3),
    timestamp=True,
)

bool_fields = ("radiator_state", "scheduler_state")
Bools = namedtuple("Bools", bool_fields)


async def log_vals():
    """Log Values."""
    await asyncio.sleep(30)  # let it start
    while True:
        temp = sensor.value or -99
        packer.append(
            floats=(temp,),
            bools=Bools(radiator_hardware(), scheduler.state),
        )
        await asyncio.sleep(settings.get("temperature-log-period", 60))


asyncio.create_task(log_vals())


class API:
    async def get(self, data):
        kwargs = {
            "n": int(data.get("n", 10)),
            "skip": int(data.get("skip", 0)),
        }
        yield "["
        started = False
        for reading in packer.read(**kwargs):
            if started:
                yield ","
            enc = {
                "temperature": reading.floats[0],
                "timestamp": reading.timestamp,
            }
            enc.update({k: v for k, v in zip(bool_fields, reading.bools)})
            yield json.dumps(enc)
            started = True
        yield "]"


api = {"log": API()}


# class GraphAPI:
#     def get
