from conman import connect
from sys import print_exception

connect()

try:

    import logging
    import log

    logger = logging.getLogger(__name__)
    logger.info("Starting App")
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
