from conman import connect
from sys import stdout, print_exception

connect()

try:

    import logging

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(stdout)
    sh.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    )
    logger.addHandler(sh)
    logger.debug("Logger initialised")

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
