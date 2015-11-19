import logging
from threading import RLock, Timer
logger = logging.getLogger(__name__)

class Player(object):
    def __init__(self, nick):
        self.nick = nick
        self.heap = []

    def addCard(self, card):
        self.heap.append(card)

    def sayGame(self, serverData):
        logger.debug('say cards for ' + self.nick)
        msg = 'your turn : '
        elem = 0
        for card in self.heap:
            elem += 1
            msg += '[{}] {} '.format(elem, card)
        serverData.privmsg(self.nick, msg)

class CAHGame(object):
    def __init__(self, dispatch, channel, serverData, blackCardStack, whiteCardStack):
        self.channel = channel
        self.serverData = serverData
        self.players = []
        self.state = 'NOT_RUNNING'
        self.lockState = RLock()
        self.whiteCardStack = whiteCardStack
        self.blackCardStack = blackCardStack
        dispatch.appendCmd('join', self.joinCmd)

    def _say(self, msg):
        self.serverData.privmsg(self.channel, msg)

    def _addPlayer(self, nick):
        logger.info('add a new player : ' + nick) 
        self.players.append(Player(nick))
        self._say('{0} join the party'.format(nick))

    def joinCmd(self, serverData, channel, user, args):
        logger.info('join command called')
        with self.lockState:
            if self.state == 'NOT_RUNNING':
                logger.error('no party currently running')
                return
            for i in self.players:
                if i.nick == user:
                    logger.warning('user already registered')
                    return
            self._addPlayer(user)
 
    def _endWaitPeople(self):
        logger.info('end of timeout, check if enough people to play')
        with self.lockState:
            #if len(self.players) < 3:
            #    self.state = 'NOT_RUNNING'
            #    self._say('You need to be 3 to play, only {0} people here, stop game'.format(len(self.players)))
            #    return
            self.state = 'ROUND_START'
        logger.info('game start')
        self._giveInitialTurn()
        self._beginTurn()

    def _giveInitialTurn(self):
        logger.debug('give initial hand for each player')
        for player in self.players:
            for cardNumber in range(0,9):
                player.addCard(self.whiteCardStack.pick())

    def _beginTurn(self):
        logger.debug('begin a new turn')
        blackCard = self.blackCardStack.pick()
        self._say("sentance is : " + blackCard.printEmpty())
        for player in self.players:
            for cardNumber in range(0, blackCard.pick):
                player.addCard(self.whiteCardStack.pick())
            player.sayGame(self.serverData)

    def start(self, nick):
        logger.info('new game on channel ' + self.channel)
        self._say('Begining a new party, wait 1 min for players')
        self._addPlayer(nick)
        with self.lockState:
            Timer(10, self._endWaitPeople).start()
            self.state = 'WAIT_PEOPLE'
