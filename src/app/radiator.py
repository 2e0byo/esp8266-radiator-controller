import uasyncio as asyncio
from machine import Pin
from primitives.pushbutton import Pushbutton
from settings import settings

from .hal import buzzer, led, radiator
from .scheduler.api import (
    NextAPI,
    OnceoffAPI,
    RuleAPI,
    RulesListAPI,
    StateAPI,
    JustifyAPI,
)
from .scheduler.scheduler import DateTimeMatch, Scheduler

scheduler = Scheduler("radiator", radiator.on, radiator.off, persist=True)

if not scheduler.rules:  # first run
    scheduler.append(DateTimeMatch(hour=8, duration=60))
    scheduler.append(DateTimeMatch(hour=22, minute=30, duration=60))


button = Pushbutton(Pin(2, Pin.IN), suppress=True)


def toggle():
    scheduler.toggle(settings.get("radiator-on-time", 45))
    asyncio.create_task(buzzer.beep(duration_ms=50))


button.press_func(toggle)
api = {
    "rules": RulesListAPI(scheduler),
    "rules/<rule_id>": RuleAPI(scheduler),
    "state": StateAPI(scheduler),
    "next": NextAPI(scheduler),
    "once-off": OnceoffAPI(scheduler),
    "justify": JustifyAPI(scheduler),
}
