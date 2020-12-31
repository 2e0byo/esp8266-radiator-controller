from time import sleep

import uasyncio as asyncio
from machine import Pin, Timer

from schedules import radiator_schedule
from setup import (
    backlight_off,
    backlight_on,
    do_connect,
    init_lcd,
    read_temp,
    relay,
    rtc,
)

# setup
do_connect()
lcd = init_lcd()

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

status = []


def automate(now):
    today = days[now[3]]
    time = now[4:6]
    for schedule in radiator_schedule:
        if today in schedule["days"]:
            if schedule["on"] == time and not relay.value():
                relay.on()
                status.append("Warming")
            elif schedule["off"] == time and relay.value():
                status.remove("Warming")
                if not status:
                    relay.off()


def lcd_print_time(callback_var):
    lcd.move_to(0, 0)
    datetime = rtc.datetime()
    date = "%02i-%02i" % datetime[1:3]
    time = "%02i:%02i:%02i" % datetime[4:7]
    lcd.putstr(date + " " + time)
    automate(datetime)


display_clock_timer = Timer(-1)
display_clock_timer.init(period=1000, mode=Timer.PERIODIC, callback=lcd_print_time)
backlight_off()


def update_schedules():
    from sys import modules

    del modules["schedules"]
    del radiator_schedule
    from schedules import radiator_schedule


def thermostat(setpoint, hysteresis=1):
    """Try to use radiator as simple thermostat to keep room at constant temperature."""
    while True:
        _printed = False
        while read_temp() >= setpoint:
            if not _printed:
                print("Waiting for room to become cold enough")
                _printed = True
            await asyncio.sleep(60)
        _printed = False
        while read_temp() < setpoint + hysteresis:
            if not _printed:
                print("Turning heating on")
                _printed = True
                status.append("Heating")
                relay.on()
            sleep(60)

        status.remove("Heating")
        print("Status:", status)
        if not status:
            relay.off()
