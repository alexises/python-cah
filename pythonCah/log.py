import logging
import sys


def prepareLogging(loggingLevel):
    logger = logging.getLogger()
    logger.setLevel(loggingLevel)

    formatStr = \
        '%(asctime)s [%(levelname)-8s] %(filename)s:%(lineno)s %(message)s'
    formater = logging.Formatter(formatStr, '%H:%M:%S')

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formater)
    handler.setLevel(loggingLevel)

    logger.addHandler(handler)
