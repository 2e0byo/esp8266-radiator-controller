from utils.scheduler import DateTimeMatch, Scheduler
from datetime import datetime
import pytest
from time import localtime


time_candidates = (
    dict(weekday=3),
    dict(second=10, minute=15),
    dict(hour=9, minute=45),
    dict(year=2099, minute=7),
    dict(year=2099, weekday=3),
)


def struct_to_dict(tm_struct):
    mapping = {
        "tm_year": "year",
        "tm_mon": "month",
        "tm_hour": "hour",
        "tm_min": "minute",
        "tm_sec": "second",
        "tm_wday": "weekday",
    }
    return {v: getattr(tm_struct, k) for k, v in mapping.items()}


@pytest.mark.parametrize("params", time_candidates)
def test_weekday(params):
    match = DateTimeMatch(**params)
    n = match.next_event(0)
    d = struct_to_dict(localtime(n))
    assert {k: v for k, v in d.items() if k in params} == params


class MockHardware:
    def __init__(self):
        self.state = False

    def on(self):
        self.state = True

    def off(self):
        self.state = False


class MockDelay_ms:
    def __init__(self, delay_ms, fn):
        self._fn = fn
        self._durn = delay_ms
        self.running = True

    def stop(self):
        self.running = False

    def trigger(self):
        self.running = True

    def elapse(self):
        """Manual elapse for testing."""
        self._fn()


@pytest.fixture
def scheduler(tmp_path):
    hardware = MockHardware()
    s = Scheduler(
        "mock",
        hardware.on,
        hardware.off,
        outdir=str(tmp_path),
    )
    s._timer = MockDelay_ms(100, s._calculate)
    s._timer.stop()
    yield s, hardware


def test_toggle_scheduler(mocker, scheduler):
    time = mocker.patch("time.time")
    time.return_value = 0
    scheduler, hardware = scheduler

    assert not hardware.state
    scheduler.append_once(10)
    assert hardware.state
    assert scheduler._timer.running
    time.return_value = 600
    scheduler._timer.elapse()
    assert not hardware.state


def test_multiple_scheduler(mocker, scheduler):
    time = mocker.patch("time.time")
    time.return_value = 0
    scheduler, hardware = scheduler

    assert not hardware.state
    scheduler.append_once(10)
    scheduler.append_once(5)
    assert hardware.state
    time.return_value = 300
    scheduler._timer.elapse()
    assert hardware.state
    time.return_value = 600
    scheduler._timer.elapse()
    assert not hardware.state
