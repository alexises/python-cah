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

    def _addPlayer(self, nick):
        logger.info('add a new player : ' + nick) 
        self.players.append(Player(nick))

    def start(self, nick):
        logger.info('new game on channel ' + self.channel)
        self._addPlayer(nick)

