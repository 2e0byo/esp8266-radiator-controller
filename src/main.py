import gc
from conman import connect
from sys import print_exception

gc.enable()
connect()

try:

    import logging
    import log

    logger = logging.getLogger(__name__)
    from clock import try_sync_clock

    try_sync_clock()
    logger.info("Starting App")
    gc.collect()
    import app

except Exception as e:
    print("Falling back....")
    print_exception(e)
    connect()

    try:
        logger.error(print_exception(e))
        logger.info("Running failsafe repl.")
    except Exception:
        print_exception(e)
        print("Running failsafe repl.")
