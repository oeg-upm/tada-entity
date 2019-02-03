import logging


def set_config(logger, logdir=""):
    if logdir != "":
        handler = logging.FileHandler(logdir)
    else:
        handler = logging.FileHandler('tada.log')
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
