from config import nick, server, port, chan, ctcp, token
import logging
import sys
from glob import glob
from datetime import datetime
from cards import *
logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger.info('start app')
    logger.debug('nick : ' + nick)
    logger.debug('chan : ' + chan)
    logger.debug('ctcp : ' + ctcp)
    logger.debug('server : ' + server)
    logger.debug('port : ' + str(port))
    logger.debug('token : ' + token)

    c = BlackCardStack('./cards/OfficialBaseSet_q.json')
    d = WhiteCardStack('./cards/OfficialBaseSet_a.json')
    c._shuffle()
    d._shuffle()
    c1 = MultiStack()
    d1 = MultiStack()
    c1.addFiles(glob('./cards/*_q.json'), BlackCardStack)
    d1.addFiles(glob('./cards/*_a.json'), WhiteCardStack)
    for i in range(0, 5):
        white = d1.pick()
        black = c1.pick()
        print(white)
        print(black.printEmpty())
        if black.pick == 1:
            print(black.printSentance(white))

if __name__ == "__main__":
    main()
