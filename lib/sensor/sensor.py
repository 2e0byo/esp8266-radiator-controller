import logging

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class Sensor:
    """A sensor which is read periodically."""

    def __init__(
        self,
        *args,
        name,
        log=True,
        period=60,
        moving_average=10,
    ):
        """Initialise a new Sensor()."""
        self.name = name
        self._logger = logging.getLogger(name) if log else None
        self._val = []
        self.period = period
        self.moving_average = moving_average
        self._dead = False
        asyncio.get_event_loop().create_task(self._loop())

    def _log(self, level, *args, **kwargs):
        if self._logger:
            getattr(self._logger, level)(*args, **kwargs)

    def _dir(self):
        """Sensor is dead."""
        self._log("warning", f"Sensor {self.name} died.")
        self._dead = True
        self._val = []

    @property
    def value(self):
        """Sensor value."""
        if not self._val or self._dead:
            return None
        return sum(self._val) / len(self._val)

    def _append_val(self, x):
        nvals = len(self._val)
        ma = self.moving_average
        if nvals >= ma:
            self._val = self._val[nvals - ma :]
        self._val.append(x)

    async def read_sensor(self):
        """Read from sensor.

        Children must implement this."""
        raise NotImplementedError("Implement this")  # pragma: nocover

    async def _loop(self):
        silent_count = 0
        while True:
            try:
                res = await self.read_sensor()
                if res is None:
                    raise Exception("Sensor returned None")
                self._append_val(res)
                silent_count = 0
            except Exception as e:
                self._log("error", f"Read sensor failed: {str(e)}")
                silent_count += 1
                if silent_count > 10:
                    self._dir()

            await asyncio.sleep(self.period)


class DummySensor(Sensor):
    """Dummy implementation, for testing or experimentation."""

    def __init__(self, *args, **kwargs):
        """Initialise a new DummySensor()."""
        super().__init__(*args, **kwargs)
        self._sensor_val = None
        self._got = 0
        self._set = []
        self.sensor_vals = None

    @property
    def sensor_val(self):
        """Get sensor value."""
        self._got += 1
        return self._sensor_val

    @sensor_val.setter
    def sensor_val(self, x):
        """Set sensor value."""
        self._set.append(x)
        self._sensor_val = x

    async def read_sensor(self):
        """Read sensor"""
        if not self.sensor_vals:
            return self._sensor_val
        else:
            return next(self.sensor_vals)
