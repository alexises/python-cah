import logging

logger = logging.getLogger(__name__)

class Player(object):
    def __init__(self, nick):
        self.nick = nick

class CAHGame(object):
    def __init__(self, dispatch, channel, serverData):
        self.channel = channel
        self.serverData = serverData
        self.players = []
        self.state = 'NOT_RUNNING'
        dispatch.appendCmd('join', self.joinCmd)

    def _say(self, msg):
        self.serverData.privmsg(self.channel, msg)

    def _addPlayer(self, nick):
        logger.info('add a new player : ' + nick) 
        self.players.append(Player(nick))
        self._say('{0} join the party'.format(nick))

    def joinCmd(self, serverData, channel, user, args):
        logger.info('join command called')
        if self.state == 'NOT_RUNNING':
            logger.error('no party currently running')
            return
        for i in self.players:
            if i.nick == user:
                logger.warning('user already registered')
                return
        self._addPlayer(user)
 
    def start(self, nick):
        logger.info('new game on channel ' + self.channel)
        self._say('Begining a new party, wait 1 min for players')
        self._addPlayer(nick)
        self.state = 'WAIT_PEOPLE'
