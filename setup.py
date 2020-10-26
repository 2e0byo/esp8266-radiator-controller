from time import sleep_us

import ntptime
from esp32_gpio_lcd import GpioLcd
from machine import PWM, RTC, Pin, Timer
from secret import wifi_PSK, wifi_SSID

relay = Pin(16, Pin.OUT)
relay.off()

vo = Pin(15, Pin.OUT)
rs = Pin(5, Pin.OUT)
e = Pin(13, Pin.OUT)
d4 = Pin(12, Pin.OUT)
d5 = Pin(14, Pin.OUT)
d6 = Pin(2, Pin.OUT)
d7 = Pin(0, Pin.OUT)
a = Pin(4, Pin.OUT)

Contrast = PWM(vo)
Contrast.freq(1000)
contrast = 512
Contrast.duty(contrast)

Backlight = PWM(a)
backlight_brightness = 1023


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


def backlight_on():
    for i in range(backlight_brightness):
        Backlight.duty(i)
        sleep_us(500)


def backlight_off():
    for i in range(Backlight.duty()):
        Backlight.duty(Backlight.duty() - 1)
        sleep_us(500)


def init_lcd():
    backlight_on()
    lcd = GpioLcd(rs, e, d4, d5, d6, d7)
    lcd.clear()
    lcd.putstr("Net Thermostat")
    return lcd


rtc = RTC()
rtc.datetime()  # get date and time


def sync_clock(callback_var):
    ntptime.settime()
    rtc.datetime()


sync_clock(None)

clock_timer = Timer(-1)
clock_timer.init(period=15 * 60 * 1000, mode=Timer.PERIODIC, callback=sync_clock)
