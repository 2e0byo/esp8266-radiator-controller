from machine import Timer

from schedules import radiator_schedule
from setup import backlight_off, backlight_on, do_connect, init_lcd, relay, rtc

# setup
do_connect()
lcd = init_lcd()

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def automate(now):
    today = days[now[3]]
    time = now[4:6]
    for schedule in radiator_schedule:
        if today in schedule["days"]:
            if schedule["on"] == time and not relay.value():
                relay.on()
            elif schedule["off"] == time and relay.value():
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
