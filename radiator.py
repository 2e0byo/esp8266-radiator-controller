import ds18x20
import ntptime
import onewire
import uasyncio as asyncio
from machine import RTC, Pin

from hal import flash, relay
from schedules import radiator_schedule, thermostat_schedule

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

status = []


def tuplet_to_day_time(time_tuplet):
    day = days[time_tuplet[3]]
    time = time_tuplet[4:6]

    return day, time


def time_to_timestamp(time):
    return time[0] * 3600 + time[1] * 60


def automate():
    global status
    now = rtc.datetime()
    today, time = tuplet_to_day_time(now)
    timestamp = time_to_timestamp(time)
    for schedule in radiator_schedule:
        if today in schedule["days"]:
            if (
                timestamp > time_to_timestamp(schedule["on"])
                and "Warming" not in status
            ):
                status.append("Warming")
            elif timestamp > time_to_timestamp(schedule["off"]) and "Warming" in status:
                status.remove("Warming")

    for schedule in thermostat_schedule:
        if today in schedule["days"]:
            if (
                timestamp > time_to_timestamp(schedule["on"])
                and "Thermostat" not in status
            ):
                status.append("Thermostat")
                asyncio.get_event_loop().create_task(thermostat(schedule["setpoint"]))
            elif (
                timestamp > time_to_timestamp(schedule["off"])
                and "Thermostat" in status
            ):
                status.remove("Thermostat")


async def thermostat(setpoint, hysteresis=1):
    """Try to use radiator as simple thermostat to keep room at constant temperature."""
    global status
    while "Thermostat" in status:
        _printed = False
        temp = await read_temp()
        while temp >= setpoint:
            if not _printed:
                print("Waiting for room to become cold enough")
                _printed = True
            await asyncio.sleep(60)
        _printed = False
        temp = await read_temp()
        while temp < setpoint + hysteresis:
            if not _printed:
                print("Turning heating on")
                _printed = True
                status.append("Heating")
                relay.on()
            await asyncio.sleep(60)

        status.remove("Heating")
        print("Status:", status)


ow = onewire.OneWire(Pin(13))
ds = ds18x20.DS18X20(ow)
roms = None


async def read_temp():
    global roms
    if not roms:
        roms = ds.scan()
    ds.convert_temp()
    await asyncio.sleep_ms(750)
    return ds.read_temp(roms[0])


async def relay_control():
    while True:
        if status:
            relay.on()
        else:
            relay.off()
        await asyncio.sleep(1)


rtc = RTC()
rtc.datetime()


async def sync_clock():
    while True:
        ntptime.settime()
        rtc.datetime()
        await asyncio.sleep(120)


async def check_schedules():
    while True:
        automate()
        await asyncio.sleep(60)


async def toggle_pulse_radiator():
    global status
    if not status:
        print("Starting Manual")
        status.append("Manual")
        asyncio.get_event_loop().create_task(blink_status())
        await asyncio.sleep(60 * 60)
        status.remove("Manual")
        print("Stopping Manual")
    else:
        status = []
        asyncio.get_event_loop().create_task(blink_status())


def toggle_thermostat():
    global status
    if "Thermostat" not in status:
        status.append("Thermostat")
        print("starting thermostat")
        asyncio.get_event_loop().create_task(thermostat(20))
    else:
        print("stopping thermostat")
        status.remove("Thermostat")

    asyncio.get_event_loop().create_task(blink_status())


async def blink_status():
    print("Blinking status", status)
    if "Thermostat" in status:
        await flash("red", 1)
    if "Warming" in status or "Manual" in status:
        await flash("green", 1)

    elif not status:
        for i in range(3):
            await flash("red", 0.1)


asyncio.get_event_loop().create_task(relay_control())
asyncio.get_event_loop().create_task(sync_clock())
asyncio.get_event_loop().create_task(check_schedules())
