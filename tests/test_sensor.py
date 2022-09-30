import asyncio

import pytest
from sensor.sensor import DummySensor


async def sleep_ms(val):
    await asyncio.sleep(val / 1_000)


@pytest.fixture
def sensor():
    d = DummySensor(name="dummy", period=0.000001)
    d.sensor_val = 0
    return d


async def test_val(sensor):
    sensor.sensor_val = 100
    await sleep_ms(1)
    assert sensor.value == 100


async def test_average(sensor):
    sensor.sensor_vals = iter([55, 45] * 1_000)
    await sleep_ms(5)
    assert sensor.value == pytest.approx(50, 1)
    sensor.sensor_vals = iter([50, 50, 50, 50, 55] * 1_000)
    assert sensor.value == pytest.approx(50, 1)


async def test_die(sensor, mocker):
    read_sensor = mocker.AsyncMock()
    read_sensor.side_effect = Exception()
    mocker.patch.object(sensor, "read_sensor", read_sensor)
    assert sensor.value == 0
    await sleep_ms(10)
    read_sensor.assert_awaited()
    assert sensor.value is None
    assert sensor.sensor_val == 0  # last set val


async def test_implicit_die(sensor, mocker):
    read_sensor = mocker.AsyncMock()
    read_sensor.return_value = None
    mocker.patch.object(sensor, "read_sensor", read_sensor)
    assert sensor.value == 0
    await sleep_ms(10)
    read_sensor.assert_awaited()
    assert sensor.value is None
    assert sensor.sensor_val == 0  # last set val


async def test_die_no_log(mocker):
    period = 0.000001
    sensor = DummySensor(name="dummy", log=False, period=period)
    sensor.sensor_val = 0
    read_sensor = mocker.AsyncMock()
    read_sensor.side_effect = Exception()
    await asyncio.sleep(period)
    assert sensor.value == 0
    sensor.read_sensor = read_sensor
    await sleep_ms(2)
    read_sensor.assert_awaited()
    assert sensor.value is None
    assert sensor.sensor_val == 0  # last set val
