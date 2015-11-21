from ircbot import SingleServerIRCBot
from config import nick, server, port, chan, ctcp, token
import logging
import sys
import traceback
from glob import glob
from datetime import datetime
from dispatch import BaseGameDispatch
logger = logging.getLogger(__name__)


def printEntry(c, e):
    """printEntry : print a line of public channel"""
    date = datetime.now()
    dateTxt = date.__format__('%H:%M:%S')
    chan = e.target()
    user = e.source().split('!')[0]
    msg = e.arguments()[0]
    print '{0} {1} <{2}> {3}'.format(dateTxt, chan, user, msg)

class CahBot(SingleServerIRCBot):
    def __init__(self, channel, nick, ctcp, server, dispatcher, port=6667, ssl=False, token='!'):
        SingleServerIRCBot.__init__(self, [(server, port)], nick, ctcp)
        self.ctcp = ctcp
        self.channel = channel
        self.ssl = ssl
        self.token = token
        self.dispatcher = dispatcher

    def _connect(self):
        password = None
        if len(self.server_list[0]) > 2:
            password = self.server_list[0][2]
        self.connect(self.server_list[0][0],
                     self.server_list[0][1],
                     self._nickname,
                     password,
                     ircname=self._realname,
                     ssl=self.ssl)

    def on_nicknameinuse(self, c, e):
        logger.warning('nick already in use, try another')
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        logger.info('welcome ok : join chan')
        logger.debug('join chan : ' + self.channel)
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.on_pubmsg(c, e)
 
    def on_pubmsg(self, c, e):
        printEntry(c, e)
        msg = e.arguments()[0]
        token = msg[0]
        chan = e.target()
        user = e.source().split('!')[0]
        if chan[0] != '#':
           chan = ''
        logger.debug('new msg')
        if token != self.token:
            logger.debug('not a command, avoid')
            return
        #filter empty component, like have two space 
        #between cmd arguments
        cmdComponents = filter(None, msg[1:].split(' '))
        if len(cmdComponents) < 1:
            logger.debug('only a token')
            return
        cmd = cmdComponents[0]
        self.dispatcher.dispatch(c, chan, user, cmd, cmdComponents[1:])
        

    def get_version(self):
        return self.ctcp

def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logger.info('start app')
    logger.debug('nick : ' + nick)
    logger.debug('chan : ' + chan)
    logger.debug('ctcp : ' + ctcp)
    logger.debug('server : ' + server)
    logger.debug('port : ' + str(port))
    logger.debug('token : ' + token)
    BlackCardsFile = glob('./cards/*_q.json')
    WhiteCardsFile = glob('./cards/*_a.json')
    dispatch = BaseGameDispatch(BlackCardsFile, WhiteCardsFile)
    try:
        bot = CahBot(chan, nick, ctcp, server, dispatch, port, ssl=True, token=token)
        bot.start()
    except KeyboardInterrupt:
        print "CTRL + C hit, close the bot"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)
if __name__ == "__main__":
    main()
