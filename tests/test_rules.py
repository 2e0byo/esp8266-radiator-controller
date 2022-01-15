import pytest
from scheduler.scheduler import DateTimeMatch, TimeDiff
from time import localtime, mktime
from json import loads

from datetime import datetime

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


def test_repr():
    match = DateTimeMatch(minute=1)
    assert (
        repr(match)
        == f"DateTimeMatch(second=0, minute=1, hour=0, duration=None, id={match.id})"
    )


@pytest.mark.xfail
def test_exclude_ranges():
    exclude = ((DateTimeMatch(hour=10), DateTimeMatch(hour=11)),)
    match = DateTimeMatch(minute=1, exclude_ranges=exclude)
    now = mktime((2000, 1, 1, 10, 0, 0, 0, 1, 0))
    next_ = match.calc_next_event(now)
    assert localtime(next_).tm_hour == 11


def test_impossible():
    match = DateTimeMatch(second=85)
    with pytest.raises(RuntimeError):
        match.next_event


def test_to_json():
    match = DateTimeMatch(minute=1, month=4, duration=1)
    id = match.id
    assert loads(match.to_json()) == dict(
        duration=1, once_off=False, id=id, second=0, minute=1, hour=0, month=4
    )
    assert loads(match.to_json(id=False)) == dict(
        duration=1, once_off=False, second=0, minute=1, hour=0, month=4
    )


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
    calc_next_event = match.next_event
    assert calc_next_event - now == 60
    assert match.next_event == calc_next_event


@pytest.mark.parametrize(
    "seconds, output, timestr",
    (
        (1, dict(seconds=1), "1 second"),
        (59, dict(seconds=59), "59 seconds"),
        (61, dict(seconds=1, minutes=1), "1 minute 1 second"),
        (60 * 60 + 61, dict(hours=1, minutes=1, seconds=1), "1 hour 1 minute 1 second"),
        (
            60 * 60 * 2 + 60 * 2 + 1,
            dict(hours=2, minutes=2, seconds=1),
            "2 hours 2 minutes 1 second",
        ),
        (60 * 60 * 24, dict(days=1), "1 day"),
        (
            60 * 60 * 24 * 2 + 60 * 60 * 2 + 62,
            dict(days=2, hours=2, minutes=1, seconds=2),
            "2 days 2 hours 1 minute 2 seconds",
        ),
    ),
)
def test_TimeDiff(seconds, output, timestr):
    t = TimeDiff(seconds)
    assert {k: v for k, v in t.diff._asdict().items() if v} == output
    assert str(t) == timestr
    j = t.to_json()
    assert loads(t.to_json()) == t.diff._asdict()  # micropython has no _asdict
