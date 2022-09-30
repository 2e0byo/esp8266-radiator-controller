import uasyncio as asyncio
from ds18x20 import DS18X20
from machine import Pin
from onewire import OneWire
from sensor import Sensor
from settings import settings


class TempSensor(Sensor):
    def __init__(self, pin, **kwargs):
        ow = OneWire(pin)
        sens = DS18X20(ow)
        self.rom = sens.scan()[0]
        self.sens = sens
        super().__init__(**kwargs)

    async def read_sensor(self):
        sens = self.sens
        sens.convert_temp()
        await asyncio.sleep(1)
        val = sens.read_temp(self.rom)
        return val


sensor_pin = Pin(13)
sensor = TempSensor(
    sensor_pin,
    name="RoomTemp",
    period=settings.get("temperature-period", 5),
)
