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
