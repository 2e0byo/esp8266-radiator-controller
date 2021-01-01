import uasyncio as asyncio
from machine import Pin
from mqtt_as import MQTTClient
from utime import time

import radiator
import sound
from config import config
from primitives.pushbutton import Pushbutton

button = Pushbutton(Pin(2, Pin.IN), suppress=True)

SERVER = "voyage.lan"

last_timestamp = None


def callback(topic, msg, retained):
    """Callback for messages."""
    global last_timestamp
    print(topic, msg, retained)
    if "sound" in msg.decode():
        ring("alarm")
    if "keepalive" in msg.decode():
        last_timestamp = time()


def ring(reason):
    if "timeout" in reason:
        print("sounding")
        asyncio.get_event_loop().create_task(sound.ring())
    else:
        asyncio.get_event_loop().create_task(sound.siren())


def stop_alarm():
    print("Stopping alarm")
    if sound.sounding:
        sound.sound = False


button.double_func(
    stop_alarm,
)
button.press_func(
    radiator.toggle_pulse_radiator,
)


async def conn_han(client):
    await client.subscribe("motorcycle_alarm", 1)


async def main(client):
    await client.connect()
    while True:
        # timeout
        if last_timestamp and (time() - last_timestamp > 80):
            ring("timeout")
        await asyncio.sleep(10)


config["subs_cb"] = callback
config["connect_coro"] = conn_han
config["server"] = SERVER

MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
