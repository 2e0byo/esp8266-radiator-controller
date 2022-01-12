from utils.scheduler import DateTimeMatch, Scheduler
from datetime import datetime
import pytest
from time import localtime, mktime


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
    n = match.calc_next_event(0)
    d = struct_to_dict(localtime(n))
    assert {k: v for k, v in d.items() if k in params} == params


def test_next(mocker):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    match = DateTimeMatch(minute=1)
    calc_next_event = match.calc_next_event()
    assert calc_next_event - now == 60


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
    assert scheduler.state
    assert scheduler._timer.running
    time.return_value = 600
    scheduler._timer.elapse()
    assert not hardware.state
    assert not scheduler.state


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


def test_pop_once(mocker, scheduler):
    time = mocker.patch("time.time")
    time.return_value = 0
    scheduler, hardware = scheduler

    assert not hardware.state
    scheduler.append_once(10)
    assert hardware.state
    scheduler.pop_once()
    assert not hardware.state


def test_rule(mocker, scheduler):

    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now

    match = DateTimeMatch(minute=1)
    assert match.calc_next_event() - now == 60

    scheduler, hardware = scheduler

    assert not hardware.state
    scheduler.append(match, 10)  # on 10 mins

    assert match.calc_next_event() - now == 60
    assert not hardware.state
    time.return_value += 61
    scheduler._timer.elapse()
    assert hardware.state
    assert scheduler._timer.running

    time.return_value += 5 * 60
    scheduler._timer.elapse()
    assert hardware.state

    time.return_value += 5 * 60
    scheduler._timer.elapse()
    assert not hardware.state


def test_append_remove(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    match = DateTimeMatch(minute=1)

    scheduler.append(match, 10)
    time.return_value += 61
    scheduler._timer.elapse()
    assert scheduler._in_progress

    scheduler.remove(match)
    assert not scheduler._in_progress


def test_pop_once_still_on(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    assert not hardware.state
    scheduler.append_once(10)
    assert hardware.state

    match = DateTimeMatch(minute=1)
    scheduler.append(match, 10)
    time.return_value += 61
    scheduler._timer.elapse()

    assert hardware.state, "Turned off after adding rule"
    scheduler.pop_once()
    assert hardware.state, "Turned off when removed one time"
    scheduler.remove(match)
    assert not hardware.state


def test_load_save(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    assert not hardware.state

    match = DateTimeMatch(minute=1)
    match2 = DateTimeMatch(minute=2)
    scheduler.append(match, 10)
    scheduler.append(match2, 10)
    scheduler.save()

    time.return_value += 61
    scheduler._timer.elapse()
    assert hardware.state
    scheduler.remove(match)
    assert not hardware.state
    time.return_value += 61
    scheduler._timer.elapse()
    assert hardware.state

    hardware = MockHardware()
    s = Scheduler(
        "mock",
        hardware.on,
        hardware.off,
        outdir=scheduler.outdir,
        persist=True,
    )
    s._timer = MockDelay_ms(100, s._calculate)
    s._timer.stop()
    assert not hardware.state
    now = mktime((2000, 1, 2, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    time.return_value += 61
    s._timer.elapse()
    assert hardware.state
    s.remove(match)
    assert not hardware.state
    time.return_value += 61
    s._timer.elapse()
    assert hardware.state


def test_once_off(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    match = DateTimeMatch(minute=1, once_off=True)
    scheduler.append(match, 1)
    time.return_value += 61
    scheduler._timer.elapse()
    assert hardware.state
    time.return_value += 61
    scheduler._timer.elapse()
    assert not hardware.state
    assert not scheduler._rules
