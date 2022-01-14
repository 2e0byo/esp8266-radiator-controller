import json
import logging
from sys import stdout

from packing.text import RotatingLog

from settings import settings

rotating_log = RotatingLog(
    "syslog",
    "static/",
    log_lines=settings.get("syslog_lines", 200),
    keep_logs=2,
    timestamp=True,
)


class RotatingLogHandler(logging.Handler):
    def __init__(self, log):
        super().__init__()
        self.log = log

    def emit(self, record):
        if record.levelno >= self.level:
            self.log.append(self.formatter.format(record))


logging.basicConfig(level=logging.DEBUG)

rotating_handler = RotatingLogHandler(rotating_log)
rotating_handler.setLevel(logging.INFO)
rotating_handler.setFormatter(
    logging.Formatter("%(name)s - %(levelname)s: %(message)s")
)

sh = logging.StreamHandler(stdout)
sh.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
)
sh.setLevel(logging.DEBUG)

logging.root.handlers.clear()
logging.root.addHandler(sh)
logging.root.addHandler(rotating_handler)

logger = logging.getLogger(__name__)
logger.debug("Logger initialised")


class API:
    def __init__(self, rotating_log):
        self._log = rotating_log

    async def get(self, data):
        kwargs = {
            "n": int(data.get("n", 10)),
            "skip": int(data.get("skip", 0)),
        }
        yield "["
        started = False
        for i, timestamp, line in self._log.read(**kwargs):
            if started:
                yield ","
            yield json.dumps(
                {"line": line.replace("\n", "\\n"), "timestamp": timestamp, "id": i}
            )
            started = True
        yield "]"


api = API(rotating_log)
