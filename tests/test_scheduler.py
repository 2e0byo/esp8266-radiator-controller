from scheduler.scheduler import Scheduler, DateTimeMatch
from datetime import datetime
import pytest
from time import localtime, mktime


def nullfn():
    pass


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
    s._timer = MockDelay_ms(100, s._recalculate)
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
    assert not scheduler.state
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

    match = DateTimeMatch(minute=1, duration=10)
    assert match.calc_next_event() - now == 60

    scheduler, hardware = scheduler

    assert not hardware.state
    scheduler.append(match)

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
    match = DateTimeMatch(minute=1, duration=10)

    scheduler.append(match)
    time.return_value += 61
    scheduler._timer.elapse()
    assert scheduler._in_progress

    scheduler.remove(match)
    assert not scheduler._in_progress


def test_remove_by_id(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    match1 = DateTimeMatch(minute=1, duration=10)
    match2 = DateTimeMatch(minute=30, duration=10)
    scheduler.append(match1)
    scheduler.append(match2)

    time.return_value += 61
    scheduler._timer.elapse()
    assert scheduler._in_progress

    # Check that removing a nonexistent rule doesn't cause duplication
    assert len(scheduler.rules) == 2
    assert len(scheduler._in_progress) == 1
    _id = max(x.id for x in scheduler.rules) + 1
    scheduler.remove_by_id(_id)
    assert len(scheduler.rules) == 2
    assert len(scheduler._in_progress) == 1
    assert len(scheduler.rules) == 2

    scheduler.remove_by_id(match1.id)
    assert not scheduler._in_progress


def test_pop_once_still_on(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    assert not hardware.state
    scheduler.append_once(10)
    assert hardware.state

    match = DateTimeMatch(minute=1, duration=10)
    scheduler.append(match)
    time.return_value += 61
    scheduler._timer.elapse()

    assert hardware.state, "Turned off after adding rule"
    scheduler.pop_once()
    assert hardware.state, "Turned off when removed one time"
    scheduler.remove(match)
    assert not hardware.state


def test_auto_save(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()

    s = Scheduler(
        "mock",
        nullfn,
        nullfn,
        outdir=str(a),
        persist=False,
    )
    match = DateTimeMatch(minute=1, duration=10)
    match2 = DateTimeMatch(minute=2, duration=10)
    s.append(match)
    s.append(match2)
    s.save()
    fn = s.fn

    s = Scheduler(
        "mock",
        nullfn,
        nullfn,
        outdir=str(b),
        persist=True,
    )
    s.append(match)
    s.append(match2)
    with open(fn) as f, open(s.fn) as g:
        assert f.read() == g.read()


def test_load_save(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    assert not hardware.state

    scheduler.persist = False
    match = DateTimeMatch(minute=1, duration=10)
    match2 = DateTimeMatch(minute=2, duration=10)
    scheduler.append(match)
    scheduler.append(match2)
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

    s._timer = MockDelay_ms(100, s._recalculate)
    s._timer.stop()
    assert not hardware.state

    now = mktime((2000, 1, 2, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    time.return_value += 61
    s._timer.elapse()

    assert hardware.state

    new_match = next(x for x in s.rules if x._spec["minute"] == 1)
    s.remove(new_match)

    assert not hardware.state
    time.return_value += 61
    s._timer.elapse()
    assert hardware.state


def test_once_off(mocker, scheduler):
    time = mocker.patch("time.time")
    now = mktime((2000, 1, 1, 0, 0, 0, 0, 1, 0))
    time.return_value = now
    scheduler, hardware = scheduler
    match = DateTimeMatch(minute=1, once_off=True, duration=1)
    scheduler.append(match)
    time.return_value += 61
    scheduler._timer.elapse()
    assert hardware.state
    time.return_value += 61
    scheduler._timer.elapse()
    assert not hardware.state
    assert not scheduler._rules


def test_justify(scheduler):
    scheduler, hardware = scheduler
    scheduler.append_once(10)
    ret = scheduler.justify()
    assert ret["state"]
    assert len(ret["in_progress"]) == 1
    assert not ret["rules"]
    assert not ret["in_progress_next_events"]
    assert not ret["rules_next_events"]


def test_failed_load(tmp_path, capsys, caplog):

    s = Scheduler("mock", nullfn, nullfn, outdir=str(tmp_path), logging=True)
    s.load()
    captured = capsys.readouterr()
    assert "FileNotFound" in captured.err
    assert any("Failed to load rules" in x.message for x in caplog.records)


def test_repr():
    s = Scheduler("mock", nullfn, nullfn, logging=False)
    assert repr(s) == "Scheduler(name=mock, self=None, rules=[], in_progress=[])"
