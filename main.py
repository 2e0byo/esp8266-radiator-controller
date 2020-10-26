from time import sleep_ms

from esp32_gpio_lcd import GpioLcd
from machine import PWM, Pin
from secret import wifi_PSK, wifi_SSID

relay = Pin(16, Pin.OUT)
relay.off()


def do_connect():
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(wifi_SSID, wifi_PSK)
        while not wlan.isconnected():
            pass
    print("network config:", wlan.ifconfig())


do_connect()


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


def backlight_on():
    for i in range(backlight_brightness):
        Backlight.duty(i)
        sleep_ms(1)


def backlight_off():
    for i in range(Backlight.duty()):
        Backlight.duty(Backlight.duty() - 1)
        sleep_ms(1)


backlight_on()


lcd = GpioLcd(rs, e, d4, d5, d6, d7)
lcd.clear()
lcd.putstr("Net Thermostat")


days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

radiator_schedule = [
    {"days": ["mon", "tue", "wed", "thu", "fri"], "on": (8, 30), "off": (9, 30)},
    {"days": ["sat", "sun"], "on": (9, 30), "off": (10, 30)},
    {
        "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "on": (23, 20),
        "off": (0, 0),
    },
]


def automate(now):
    today = days[now[3]]
    time = now[4:6]
    for schedule in radiator_schedule:
        if today in schedule["days"]:
            if schedule["on"] == time and not relay.value():
                relay.on()
            elif schedule["off"] == time and relay.value():
                relay.off()


from machine import RTC

rtc = RTC()
rtc.datetime()  # get date and time

# synchronize with ntp
# need to be connected to wifi
import ntptime


def sync_clock(callback_var):
    ntptime.settime()
    rtc.datetime()


sync_clock(None)

from machine import Timer

clock_timer = Timer(-1)
clock_timer.init(period=15 * 60 * 1000, mode=Timer.PERIODIC, callback=sync_clock)


def lcd_print_time(callback_var):
    lcd.move_to(0, 0)
    datetime = rtc.datetime()
    date = "%02i-%02i" % datetime[1:3]
    time = "%02i:%02i:%02i" % datetime[4:7]
    lcd.putstr(date + " " + time)
    automate(datetime)


display_clock_timer = Timer(-1)
display_clock_timer.init(period=1000, mode=Timer.PERIODIC, callback=lcd_print_time)
