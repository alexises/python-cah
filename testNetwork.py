from io import IrcClient
import logging
import sys

logger = logging.getLogger(__name__)
def test():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger.info('start app')
    client = IrcClient('irc.iiens.net', 7000, 'cahBot', 'cahBot', ssl = True, sslCheck = False)
    client.addChannel('#jeux')
    client.addChannel('#cahBot')
    client.connect()

if __name__ == '__main__':
   test()
