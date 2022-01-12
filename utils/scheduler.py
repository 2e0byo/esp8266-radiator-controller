import time
import json
from logging import getLogger

try:
    from primitives.delay_ms import Delay_ms
except ImportError:
    from unittest.mock import MagicMock

    Delay_ms = MagicMock()


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

    def __init__(self, exclude_ranges=None, once_off=False, **kwargs):
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
            while time.localtime(target)[i] != spec[unit]:
                target += length

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
        self._timer = Delay_ms(100, self._calculate)
        self._calculate()
        self._timer.stop()
        if persist:
            self.load()
        super().__init__(**kwargs)

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
                    d.duration = rule["duration"]
                    self._rules.append(d)
            self._recalculate()
        except OSError:
            pass

    def save(self):
        data = [
            dict(args=d._spec, duration=d.duration)
            for d in self._rules
            if not d.once_off
        ]
        with open(self.fn, "w") as f:
            json.dump(data, f)

    def remove(self, rule):
        self._rules = [x for x in self._rules if repr(x) != repr(rule)]
        self._in_progress = [x for x in self._in_progress if repr(x[0]) != repr(rule)]
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
        if not self._in_progress and not self._rules:
            self._calculate()
            return

        nearest = [x[1] for x in self._in_progress]
        nearest += [x.next_event for x in self._rules]
        nearest = min(nearest)
        diff = nearest - time.time() + 1
        self._timer.stop()
        if self._logger:
            self._logger.debug(f"Next wake up in {diff} seconds")
        self._timer._durn = diff * 1_000
        self._calculate()
        self._timer.trigger()

    def _calculate(self):
        now = time.time()

        # drop stale reasons to be on
        in_progress = []
        for rule, elapse in self._in_progress:
            if elapse <= now:
                if not rule:
                    continue
                elif rule.once_off:
                    self._rules.remove(rule)
            else:
                in_progress.append((rule, elapse))

        self._in_progress = in_progress

        # trigger any rule which should run now
        for rule in self._rules:
            start = rule.next_event
            if (
                abs(start - now) < 10
            ):  # allow 10s error: assumes no rules closer than that
                self._in_progess.append((rule, now + rule.duration))
                rule.calc_next_event()

        if not self._in_progress:
            self._off()
        else:
            self._on()
