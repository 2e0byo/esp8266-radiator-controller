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

ringing = False


def callback(topic, msg, retained):
    """Callback for messages."""
    global last_timestamp
    print(topic, msg, retained)
    if "sound" in msg.decode():
        ring("alarm")
    if "keepalive" in msg.decode():
        last_timestamp = time()


def ring(reason):
    global ringing
    if ringing:
        return
    if "timeout" in reason:
        print("sounding")
        asyncio.get_event_loop().create_task(sound.ring())
        ringing = True
    else:
        asyncio.get_event_loop().create_task(sound.siren())
        ringing = True


def stop_alarm():
    global ringing
    print("Stopping alarm")
    if sound.sounding:
        sound.sound = False
    ringing = False


button.double_func(
    stop_alarm,
)
button.release_func(
    radiator.toggle_pulse_radiator,
)

button.long_func(
    radiator.toggle_thermostat,
)


async def conn_han(client):
    await client.subscribe("motorcycle_alarm", 1)


async def main(client):
    await client.connect()
    while True:
        # timeout
        if last_timestamp and (time() - last_timestamp > 180):
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
