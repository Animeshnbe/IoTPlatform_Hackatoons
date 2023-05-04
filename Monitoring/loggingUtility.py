import logging
from logging.handlers import TimedRotatingFileHandler


def logger_func():
    logging.basicConfig(filename="log.txt", format="%(asctime)s %(message)s", filemode="w")
    logger = logging.getLogger()

    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)
    return logger
# logging.debug("Logging test...")
# logging.info("The program is working as expected")
# logging.warning("The program may not function properly")
# logging.error("The program encountered an error")
# logging.critical("The program crashed")


def init_logging(log_file="log.log"):
    fmt = "%(asctime)s - %(pathname)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if log_file:
        handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
    else:
        handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
