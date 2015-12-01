from io import MultiIrcClient
import logging
logger = logging.getLogger(__name__)

class CahBot(MultiIrcClient):
    def __init__(self, config, dispatcher):
        self.config = config
        super(CahBot, self).__init__(self.config.serverList())
        self.dispatcher = dispatcher

    def notice(self, server, sender, destination, message):
        self.privmsg(server, sender, destination, message)

    def privmsg(self, server, sender, destination, message):
        tokenToCheck = self.config[server][destination].token
        token = message[0]
        chan = destination
        user = sender.split('!')[0]
        if destination[0] != '#':
            chan = ''
        logger.debug('new msg')
        if token != tokenToCheck:
            logger.debug('not a command, avoid')
            return
        #filter empty component, like have two space
        #between cmd arguments
        cmdComponents = filter(None, msg[1:].split(' '))
        if len(cmdComponents) < 1:
            logger.debug('only a token')
            return
        cmd = cmdComponents[0]
        self.dispatcher.dispatch(server, chan, user, cmd, cmdComponents[1:])
