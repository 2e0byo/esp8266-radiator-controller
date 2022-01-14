import logging
from packing.text import RotatingLog
from settings import settings
from sys import stdout


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
