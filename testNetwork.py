from io import IrcClient
import logging
import sys

logger = logging.getLogger(__name__)
def test():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger.info('start app')
    client = IrcClient('irc.freenode.net', 6667, 'cahBot', 'cahBot')
    client.connect()

if __name__ == '__main__':
   test()
