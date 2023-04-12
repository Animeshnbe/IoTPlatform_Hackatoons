import logging


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
