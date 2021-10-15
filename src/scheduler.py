import time
import json

try:
    import asyncio
except:
    import uasyncio as asyncio


class DateTimeMatch:
    _UNITS = {
        "second": (1, 5),
        "minute": (60, 4),
        "hour": (60 * 60, 3),
        "day": (24 * 60 * 60, 2),
        "month": (28 * 24 * 60 * 60, 1),
        "year": (365 * 24 * 60 * 60, 0),
        "weekday": (24 * 60 * 60, 6),
    }

    def __init__(self, exclude_ranges=None, **kwargs):
        # exclude_ranges is a list of DateTimeMatch objects in tuples (start, end) and is inclusive
        self._spec = {
            "second": 0,
            "minute": 0,
            "hour": 0,
        }
        self._spec.update(kwargs)
        print(self._spec)
        if exclude_ranges:
            raise NotImplementedError("Exclude ranges not yet implemented")

    @classmethod
    def time_to_dict(cls, t):
        return dict(zip(DateTimeMatch._UNITS.keys(), t[:7]))

    def next_event(self, target=None):
        target = target or time.time()
        spec = self._spec
        # calculate minimum distance to next event
        now = target
        for unit, (length, i) in self._UNITS.items():
            if unit not in self._spec:
                continue

            while time.localtime(target)[i] != spec[unit]:
                target += length

        return target


# d = DateTimeMatch(day=15, hour=12, minute=37)
# d = DateTimeMatch(minute=12)
# print(time.localtime(time.time() + d.next_event()))


class Scheduler:
    def __init__(self, name, prop, persist=False, outdir=".", **kwargs):
        self._name = name
        self._prop = prop
        self._rules = []
        self._in_progress[]
        self._timer = Delay_ms(self._stop_warm, self.elapse)
        self._timer.stop()
        if persist:
            self.load()
        super().__init__(**kwargs)

    @property
    def fn(self):
        return f"{self.outdir}/{self._name}_schedule.json"

    def load(self):
        with open(self.fn) as f:
            data = json.load(f)
            for rule in data:
                d = DateTimeMatch(**data["args"])
                d.duration = rule["duration"]
                self._rules.append(d)

    def save(self):
        data = [dict(args=d._spec, duration=d.duration) for d in self._rules]
        with open(self.fn) as f:
            f.write(json.dump(data))

    def append(self, d, duration):
        d.duration = duration
        self._rules.append(d)
        self._recalculate()

    def _recalculate(self):
        nearest = min(self._rules, key=lambda d: d.next_event())
        nearest = min(nearest, self._in_progress)
        diff = nearest.next_event() - time.time() + 1
        self._timer.stop()
        self._timer._durn = diff * 1_000
        self._timer.start()

    def _calculate(self):
        now = time.time()
        # drop stale reasons to be on
        self._in_progess = [x for x in self._in_progress if x > now]
        # trigger any rule which should run now
        for rule in self._rules:
            start = rule.next_event()
            if abs(start - now) < 10: # allow 10s error: assumes no rules closer than that
                self._in_progess.append(now+rule.duration)

        if not self._in_progress:
            self.prop = False
        else:
            self.prop = True


class OtherScheduler:
    def __init__(self, name, functions, persist=False, outdir="."):
        self._name = name
        self._events = []
        self._functions = {fn.__name__: fn for fn in functions}
        self._timer = Delay_ms(self._stop_warm, self.elapse)
        self._timer.stop()
        self._next_event = None
        if persist:
            self.load()
        asyncio.get_event_loop().create_task(self._loop())

    @property
    def fn(self):
        return f"{self.outdir}/{self._name}_schedule.json"

    def load(fn):
        # load, ignoring events referring to functions we don't have
        with open(self.fn) as f:
            self._events = {
                k: v for k, v in json.load(f) if v in self._functions.keys()
            }

    @property
    def events(self):
        return self._events

    def add_event(self, t, fn):
        if fn not in self._functions.keys():
            raise ValueError(f"Supplied function name {fn} not known.")
        t._function = self._functions[fn]
        self._events.append(t)
        self.update()

    def next(self):
        return min(x.next_event() for x in self._events) if self._events else None

    def update(self):
        self._timer.stop()
        ev = min(self._events, key=lambda x: x.next_event())
        self._timer._durn = (ev.next_event() - time.time()) * 1_000
        self._next_event = self._functions[ev._function]
        self._timer.start()

    def elapse():
        self._next_event()
        self._update()
