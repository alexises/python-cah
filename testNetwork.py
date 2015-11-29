from io import NonBlockingIrcClient
import logging
import sys

logger = logging.getLogger(__name__)
def test():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger.info('start app')
    client = NonBlockingIrcClient('irc.iiens.net', 7000, 'cahBot', 'cahBot', ssl = True, sslCheck = False)
    client.addChannel('#jeux')
    client.addChannel('#cahBot')
    client.start()
    logger.info('client2')
    client2 = NonBlockingIrcClient('irc.freenode.net', 7000, 'cahBot', 'cahBot', ssl = True)
    client2.start()

    while 1:
        pass 
if __name__ == '__main__':
   test()
