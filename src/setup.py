from time import sleep_ms

import ds18x20
import ntptime
import onewire
from machine import PWM, RTC, Pin, Timer

from secret import wifi_PSK, wifi_SSID

relay = Pin(0, Pin.OUT)
relay.off()


led1 = Pin(16, Pin.OUT)
led2 = Pin(5, Pin.OUT)
led = PWM(led2)

duties = {"red": 0, "green": 0}
colour = "red"


def led_colour(col: str):
    global led, led1, colour, duties
    if col == "green":
        led1.off()
        led.duty(duties[col])
        colour = "green"
    elif col == "red":
        led1.on()
        led.duty(1023 - duties[col])
        colour = "red"


led_colour("red")


def led_brightness(br):
    if colour == "red":
        led.duty(1023 - br)
    else:
        led.duty(br)
    duties["colour"] = br


# turn off wifi led
# led = Pin(2, Pin.IN)


def do_connect():
    """Connect to the network."""
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(wifi_SSID, wifi_PSK)
        while not wlan.isconnected():
            pass
    print("network config:", wlan.ifconfig())


rtc = RTC()
rtc.datetime()  # get date and time


def sync_clock(callback_var):
    ntptime.settime()
    rtc.datetime()


try:
    sync_clock(None)
except OSError:
    pass

clock_timer = Timer(-1)
clock_timer.init(period=15 * 60 * 1000, mode=Timer.PERIODIC, callback=sync_clock)


ow = onewire.OneWire(Pin(0))
ds = ds18x20.DS18X20(ow)
roms = None


def read_temp():
    global roms
    if not roms:
        roms = ds.scan()
    ds.convert_temp()
    sleep_ms(750)
    return ds.read_temp(roms[0])
