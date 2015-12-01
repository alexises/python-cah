from irc import CahBot
from config import loadConfig
import logging
import sys
import traceback
from glob import glob
from datetime import datetime
from dispatch import BaseGameDispatch
logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger.info('start app')
    config = loadConfig('config.json')
    BlackCardsFile = glob('./cards/*_q.json')
    WhiteCardsFile = glob('./cards/*_a.json')
    dispatch = BaseGameDispatch(BlackCardsFile, WhiteCardsFile)
    bot = CahBot(config, dispatch)
    try:
        bot.start()
    except KeyboardInterrupt:
        print "CTRL + C hit, close the bot"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
