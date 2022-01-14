import time
import json
from logging import getLogger
from collections import namedtuple

try:
    from primitives.delay_ms import Delay_ms
except ImportError:
    from unittest.mock import MagicMock

    print("Using mocked timer")
    Delay_ms = MagicMock()


class TimeDiff:
    _SECONDS_IN_MINUTE = 60
    _SECONDS_IN_HOUR = _SECONDS_IN_MINUTE * 60
    _SECONDS_IN_DAY = _SECONDS_IN_HOUR * 24
    FIELDS = ("days", "hours", "minutes", "seconds")
    Timediff = namedtuple("Timediff", FIELDS)

    def __init__(self, seconds):
        days, seconds = divmod(seconds, self._SECONDS_IN_DAY)
        hours, seconds = divmod(seconds, self._SECONDS_IN_HOUR)
        minutes, seconds = divmod(seconds, self._SECONDS_IN_MINUTE)
        self.diff = self.Timediff(days, hours, minutes, seconds)

    def __str__(self):  # isn't python fun!
        return " ".join(
            f"{val} {fn[:-1 if val==1 else None]}"
            for val, fn in zip(self.diff, self.FIELDS)
            if val
        )


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
    instances = []

    def __init__(self, exclude_ranges=None, once_off=False, duration=None, **kwargs):
        # exclude_ranges is a list of DateTimeMatch objects in tuples (start, end) and is inclusive
        self.once_off = once_off
        self._spec = {
            "second": 0,
            "minute": 0,
            "hour": 0,
        }
        self._spec.update(kwargs)
        if exclude_ranges:
            raise NotImplementedError("Exclude ranges not yet implemented")
        self._next_event = None
        self.duration = duration
        self.id = len(self.instances) + 1
        self.instances.append(self.id)

    def to_json(self):
        d = dict(duration=self.duration)
        d.update(self._spec)
        return json.dumps(d)

    def __repr__(self):
        spec = ", ".join(f"{k}={v}" for k, v in self._spec.items())
        return f"DateTimeMatch({spec})"

    def calc_next_event(self, start=None):
        target = start or time.time()
        spec = self._spec
        # calculate minimum distance to next event
        now = target
        for unit, (length, i) in self._UNITS.items():
            if unit not in self._spec:
                continue
            attempts = 0
            while time.localtime(target)[i] != spec[unit]:
                attempts += 1
                target += length
                if attempts > 400:
                    raise RuntimeError(
                        f"Failed to calculate next event for {self} starting at {start}"
                    )

        self._next_event = target

        return target

    @property
    def next_event(self):
        if not self._next_event:
            self.calc_next_event()
        return self._next_event


class Scheduler:
    def __init__(
        self, name, on_fn, off_fn, persist=False, outdir=".", logging=True, **kwargs
    ):
        self._state = None
        self._logger = getLogger(name) if logging else None
        self.outdir = outdir
        self._name = name
        self._on_fn = on_fn
        self._off_fn = off_fn
        self._rules = []
        self._in_progress = []
        self._timer = Delay_ms(duration=100, func=self._recalculate)
        self._next_wakeup = 0
        self._timer.stop()
        if persist:
            self.load()
        super().__init__(**kwargs)

    @property
    def rules(self):
        return self._rules

    def __repr__(self):
        return f"Scheduler(name={self._name}, self={self.state}, rules={self._rules}, in_progress={self._in_progress})"

    def _on(self):
        if self._logger:
            self._logger.info(f"Turning on, was {self._state}")
        self._state = True
        self._on_fn()

    def _off(self):
        if self._logger:
            self._logger.info(f"Turning off, was {self._state}")
        self._state = False
        self._off_fn()

    @property
    def state(self):
        return self._state

    @property
    def fn(self):
        return f"{self.outdir}/{self._name}_schedule.json"

    def load(self):
        try:
            with open(self.fn) as f:
                data = json.load(f)
                for rule in data:
                    d = DateTimeMatch(**rule["args"])
                    self._rules.append(d)
            self._recalculate()
        except OSError:
            pass

    def save(self):
        data = [d.to_json() for d in self._rules if not d.once_off]
        with open(self.fn, "w") as f:
            json.dump(data, f)

    def remove(self, rule):
        _id = rule.id
        self._rules = [x for x in self._rules if x.id != _id]
        self._in_progress = [x for x in self._in_progress if x[0].id != _id]
        self._recalculate()

    def append(self, rule, duration):
        rule.duration = duration * 60
        self._rules.append(rule)
        self._recalculate()

    def append_once(self, duration):
        self._on_fn()
        self._in_progress.append((None, time.time() + duration * 60))
        self._recalculate()

    def pop_once(self):
        self._in_progress = [x for x in self._in_progress if x[0]]
        self._recalculate()

    def _recalculate(self):
        now = time.time()

        if not self._in_progress and not self._rules:
            return

        # drop stale reasons to be on
        in_progress = []
        for rule, elapse in self._in_progress:
            if elapse <= now:
                if not rule:
                    continue
                elif rule.once_off:
                    self._rules.remove(rule)
                else:
                    rule.calc_next_event()
            else:
                in_progress.append((rule, elapse))

        self._in_progress = in_progress

        # trigger any rule which should run now
        for rule in self._rules:
            start = rule.next_event
            if (
                abs(start - now) < 5
            ):  # allow 5s error: assumes no rules closer than that
                self._in_progress.append((rule, now + rule.duration))

        nearest = [x[1] for x in self._in_progress]
        nearest += [x.next_event for x in self._rules]
        nearest = min(x for x in nearest if x > now)

        self._next_wakeup = nearest
        if self._logger:
            self._logger.debug(f"Next wake up in {self.next_wakeup}")

        diff = nearest - now
        try:
            self._timer.stop()
        except RuntimeError:
            pass  # already stopped
        self._timer._durn = diff * 1_000
        self._timer.trigger()

        if not self._in_progress:
            self._off()
        else:
            self._on()

    @property
    def next_wakeup(self):
        return TimeDiff(self._next_wakeup - round(time.time()))


class RulesListAPI:
    def __init__(self, scheduler):
        self._scheduler = scheduler

    def get(self, data):
        yield "["

        started = False
        for rule in self._scheduler.rules:
            if started:
                yield ","
            yield rule.to_json()
            started = True

        yield "]"

    def post(self, data):
        if not "duration" in data:
            raise InputError("No Duration")

        if not any(x in data for x in DateTimeMatch._UNITS.keys()):
            raise InputError("No TimeSpec")
        rule = DateTimeMatch(**data)
        self._scheduler.append(rule)
