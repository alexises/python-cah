import logging
from threading import RLock, Timer
logger = logging.getLogger(__name__)

class Player(object):
    def __init__(self, nick):
        self.nick = nick
        self.heap = []
        self.score = 0

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
    
    def removeCards(self, cards):
        cards.sort()
        for index, value in enumerate(cards):
           del self.heap[value - index]

class PlayedCards(object):
    def __init__(self):
        self.heap = []

    def append(self, nick, cards):
        self.heap.append({ 'nick' : nick, 'cards' : cards})

    def shuffle(self):
        shuffle(self.heap)

    def search(self, nick):
        for i in self.heap:
            if i['nick'] == nick:
                return True
        return False

class CAHGameUtils(object):
    def __init__(self, serverData, channel):
        self.serverData = serverData
        self.channel = channel
        self.players = []

    def _sayScore(msg):
        scoreMsg = 'score : '
        for player in player:
            scorePlayerMsg = '{} : {},'.format(player.nick, player.score) 
            scoreMsg + scorePlayerMsg
        scoreMsg = scoreMsg[:-1]
        self._say(scoreMsg)

    def _say(self, msg):
        self.serverData.privmsg(self.channel, msg)

    def _privateSay(self, nick, msg):
        self.serverData.privmsg(nick, msg)

    def _addPlayer(self, nick):
        logger.info('add a new player : ' + nick) 
        self.players.append(Player(nick))
        self._say('{0} join the party'.format(nick))


class CAHGame(CAHGameUtils):
    def __init__(self, dispatch, channel, serverData, blackCardStack, whiteCardStack):
        super(CAHGame, self).__init__(serverData, channel)
        self.state = 'NOT_RUNNING'
        self.lockState = RLock()
        self.whiteCardStack = whiteCardStack
        self.blackCardStack = blackCardStack
        self.czar = -1
        dispatch.appendCmd('join', self.joinCmd)
        dispatch.appendCmd('pick', self.pickCmd)

    def joinCmd(self, serverData, channel, user, args):
        ''' 1) join a party '''
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
        ''' 2) wait all people '''
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
        ''' 3) give initial hand'''
        logger.debug('give initial hand for each player')
        for player in self.players:
            for cardNumber in range(0,9):
                player.addCard(self.whiteCardStack.pick())

    def _beginTurn(self):
        ''' 4) select the czar, pick black card, pick white card ans wait 
        for white people to play
        '''
        logger.debug('begin a new turn')
        self.playedCards = PlayedCards()
        self.czar = (self.czar + 1) % len(self.players)
        self._say("{} is the czar".format(self.players[self.czar].nick))
        self.currentBlackCard = self.blackCardStack.pick()
        self._say("sentance is : " + self.currentBlackCard.printEmpty())
        for player in self.players:
            if player == self.players[self.czar]:
                continue
            for cardNumber in range(0, blackCard.pick):
                player.addCard(self.whiteCardStack.pick())
            player.sayGame(self.serverData)

        with self.lockState:
            self.state = 'WAIT_WHITE'
        self.currenTimer = Timer(60, self._endWaitWhiteCard).start()


    def _playWhiteCards(self, serverData, channel, user, args):
        ''' 5) play white card '''
        logger.info('{} is playing white cards {}'.format(user, args))
        logger.debug('search for player')
        player = None
        for checkedPlayer in self.players:
            if checkedPlayer.nick == user:
                player = checkedPlayer
                break
        if player == None:
            logger.debug('not a player is currently play')
            return
        if self.playedCards.search(user):
            logger.debug('player have already played')
            return
        if len(args) != self.currentBlackCard.pick:
            logger.warning('played {} white card, need {}'.format(len(args), self.currentBlackCard.pick))
            self._privateSay(user, '{}: you should pick {} cards'.format(user, self.currentBlackCard.pick))
            return
        cards = []
        realArgs = []
        try:
            for i in args:
                idx = int(i)
                if idx > (9+ self.currentBlackCard.pick):
                    raise ValueError('')
                realArgs.append(idx - 1) 
                cards.append(player.heap[idx])
        except ValueError:
            self._privateSay(user, 'argument should be number between 1 and {}'.format(9+self.currentBlackCard.pick))
        player.removeCards(realArgs)
        self.playedCards.append(user, cards)
        self._privateSay(user, 'ok, your turn is in the machine')

    def _endWaitWhiteCard(self):
        ''' 6) discard lazy people that not played white card '''
        with self.lockState:
            if self.state != 'WAIT_WHITE':
               return
        logger.info('timeout for playing white card is expired')
        self._say('timeout for playing white card is expired')
        self._say("peoples that haven't played are disquilified for this turn")
        self._beginCzarTurn()    

    def _beginCzarTurn(self):
        ''' 7) show all proposition and wait for the czar decision '''
        pass

    def _selectWinner(self, serverData, channel, user, args):
        ''' 8) select the winner '''
        pass

    def pickCmd(self, serverData, channel, user, args):
        with self.lockState:
            if self.state == 'WAIT_WHITE':
                #we are on step 5
                self._playWhiteCards(serverData, channel, user, args)
            elif self.state == 'WAIT_CZAR':
                #we are on step 8
                self._selectWinner(serverData, channel, user, args)
            else:
                logger.warning('command used in bad context')
                return

    def start(self, nick):
        logger.info('new game on channel ' + self.channel)
        self._say('Begining a new party, wait 1 min for players')
        self._addPlayer(nick)
        with self.lockState:
            Timer(10, self._endWaitPeople).start()
            self.state = 'WAIT_PEOPLE'
