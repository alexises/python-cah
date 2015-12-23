import logging
from threading import RLock, Timer
from random import shuffle
from . import i18n
logger = logging.getLogger(__name__)


class Player(object):
    '''
    Player, store information about a player profile
    along the party
    '''
    def __init__(self, nick):
        self.nick = nick
        self.heap = []
        self.score = 0

    def addCard(self, card):
        self.heap.append(card)

    def sayGame(self, serverData):
        logger.debug('say cards for ' + self.nick)
        msg = i18n.hand
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
    '''
    PlayerCards : store and manage cards played during a round
    this also provide a way to shuffle the card heap before
    print them
    '''
    def __init__(self):
        self.heap = []

    def append(self, idx, nick, cards):
        logger.debug('{} ({}) had played {}'.format(nick, idx, cards))
        self.heap.append({'nick': nick, 'id': idx, 'cards': cards})

    def shuffle(self):
        shuffle(self.heap)

    def search(self, nick):
        for i in self.heap:
            if i['nick'] == nick:
                return True
        return False

    def __len__(self):
        return len(self.heap)


class CAHGameUtils(object):
    '''
    CAHGameUtils : define usefull routine used along the game
    '''
    def __init__(self, serverData, channel):
        self.serverData = serverData
        self.channel = channel
        self.players = []

    def _sayScore(self):
        scoreMsg = i18n.score
        for player in self.players:
            scorePlayerMsg = '{} : {}, '.format(player.nick, player.score)
            scoreMsg += scorePlayerMsg
        scoreMsg = scoreMsg[:-2]
        self._say(scoreMsg)

    def _say(self, msg):
        self.serverData.privmsg(self.channel, msg)

    def _privateSay(self, nick, msg):
        self.serverData.privmsg(nick, msg)

    def _addPlayer(self, nick):
        logger.info('add a new player : ' + nick)
        self.players.append(Player(nick))
        self._say(i18n.join.format(nick))


class CAHGame(CAHGameUtils):
    def __init__(self, dispatch, channel, serverData,
                 blackCardStack, whiteCardStack):
        super(CAHGame, self).__init__(serverData, channel)
        self.state = 'NOT_RUNNING'
        self.lockState = RLock()
        self.whiteCardStack = whiteCardStack
        self.blackCardStack = blackCardStack
        self.czar = -1

        dispatch.appendCmd('join', self.joinCmd)
        dispatch.appendCmd('pick', self.pickCmd)
        dispatch.appendCmd('score', self.scoreCmd)
        dispatch.appendCmd('hand', self.handCmd)
        dispatch.appendCmd('force-start', self.forceStartCmd)

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
            if len(self.players) < 3:
                self.state = 'NOT_RUNNING'
                self._say(i18n.needMorePlayers.format(len(self.players)))
                return
            self.state = 'ROUND_START'
        logger.info('game start')
        self._giveInitialTurn()
        self._beginTurn()

    def _giveInitialTurn(self):
        ''' 3) give initial hand'''
        logger.debug('give initial hand for each player')
        for player in self.players:
            for cardNumber in range(0, 9):
                player.addCard(self.whiteCardStack.pick())

    def _beginTurn(self):
        ''' 4) select the czar, pick black card, pick white card ans wait
        for white people to play
        '''
        logger.debug('begin a new turn')
        self.playedCards = PlayedCards()

        self.czar = (self.czar + 1) % len(self.players)
        self._say(i18n.czar.format(self.players[self.czar].nick))

        self.currentBlackCard = self.blackCardStack.pick()
        self._say(i18n.blackCardIs + self.currentBlackCard.printEmpty())

        for player in self.players:
            if player == self.players[self.czar]:
                continue
            for cardNumber in range(0, self.currentBlackCard.pick):
                player.addCard(self.whiteCardStack.pick())
            player.sayGame(self.serverData)

        with self.lockState:
            self.state = 'WAIT_WHITE'
        self.currentTimer = Timer(60, self._endWaitWhiteCard)
        self.currentTimer.start()

    def _playWhiteCards(self, serverData, channel, user, args):
        ''' 5) play white card '''
        logger.info('{} is playing white cards {}'\
            .format(user, args))
        logger.debug('search for player')
        player = None
        idxPlayer = -1
        for checkedPlayer in self.players:
            idxPlayer += 1
            if checkedPlayer.nick == user:
                player = checkedPlayer
                break
        if player is None:
            logger.debug('not a player is currently play')
            return
        if self.playedCards.search(user):
            logger.debug('player have already played')
            return
        if self.players[self.czar].nick == user:
            logger.warning('czar try to play a white card')
            self._say(i18n.czarCantPlay.format(user))
            return

        if len(args) != self.currentBlackCard.pick:
            nbNeededCards = self.currentBlackCard.pick
            logger.warning('played {} white card, need {}'\
                .format(len(args),nbNeededCards))
            self._privateSay(user, i18n.badNumberOfCards.format(user, nbNeededCards))
            return
        cards = []
        realArgs = []
        try:
            for i in args:
                idx = int(i)
                if idx > (9 + nbNeededCards):
                    raise ValueError('')
                realArgs.append(idx - 1)
                cards.append(player.heap[idx])
        except ValueError:
            self._privateSay(user, i18n.cardOutOfRange.format(9+nbNeededCards))

        player.removeCards(realArgs)
        self.playedCards.append(idxPlayer, user, cards)
        self._privateSay(user, i18n.pickAck)
        if len(self.playedCards) == (len(self.players) - 1):
            self._beginCzarTurn()

    def _endWaitWhiteCard(self):
        ''' 6) discard lazy people that not played white card '''
        with self.lockState:
            if self.state != 'WAIT_WHITE':
                return
        logger.info('timeout for playing white card is expired')
        self._say(i18n.timeoutWhiteCard1)
        self._say(i18n.timeoutWhiteCard2)
        self._beginCzarTurn(False)

    def _beginCzarTurn(self, normalEnd=True):
        ''' 7) show all proposition and wait for the czar decision '''
        # if all people have play before the end of the timer we should stop it
        with self.lockState:
            self.state = 'WAIT_CZAR'
            if normalEnd:
                self.currentTimer.cancel()

        self.playedCards.shuffle()
        for index, card in enumerate(self.playedCards.heap):
            sentance = self.currentBlackCard.printSentance(card['cards'])
            self._say('[{}] {}'.format(index + 1, sentance))
        self._say(i18n.czarPick.format(self.players[self.czar].nick))

    def _selectWinner(self, serverData, channel, user, args):
        ''' 8) select the winner '''
        if self.players[self.czar].nick != user:
            logger.warning('not a czar try to play a white card')
            self._say(i18n.notTheCzar.format(user))
            return
        if len(args) != 1:
            logger.warning('bad number of arguments')
            self._say(i18n.pickUsage.format(user))
            return
        card = 0
        try:
            card = int(args[0])
        except ValueError:
            self._say(i18n.pickUsage.format(user))
            return
        if card < 1 or card > len(self.playedCards):
            self._say(i18n.cardOutOfRange.format(len(self.playedCards)))
            return

        winner = self.playedCards.heap[card - 1]
        self.players[winner['id']].score += 1

        whiteCards = winner['cards']
        sentance = self.currentBlackCard.printSentance(whiteCards)
        self._say(i18n.winner.format(winner['nick'], sentance))

        self._sayScore()
        self._beginTurn()

    def pickCmd(self, serverData, channel, user, args):
        with self.lockState:
            if self.state == 'WAIT_WHITE':
                # we are on step 5
                self._playWhiteCards(serverData, channel, user, args)
            elif self.state == 'WAIT_CZAR':
                # we are on step 8
                self._selectWinner(serverData, channel, user, args)
            else:
                logger.warning('command used in bad context')
                return

    def scoreCmd(self, serverData, channel, user, args):
        '''
        scoreCmd : print the current score
        '''
        self._sayScore()

    def handCmd(self, serverData, channel, user, args):
        '''
        handCmd : print current hand
        '''
        player = None
        for checkedPlayer in self.players:
            if checkedPlayer.nick == user:
                player = checkedPlayer
                break
        if player is None:
            return
        player.sayGame(serverData)

    def forceStartCmd(self, serverData, channel, user, args):
        '''
        forceStartCmd : force the launch of the game before end of timeout
        '''
        logger.info('force start-engaged')
        if self.state != 'WAIT_PEOPLE':
            logger.error('bad state for use force-start, we are on {}, ' +
                         'expect WAIT_PEOPLE'.format(self.state))
            return
        if len(self.players) < 3:
            self._say(i18n.cantStartYet.format(len(self.players)))
        self.currentTimer.cancel()
        self._endWaitPeople()

    def start(self, nick):
        logger.info('new game on channel ' + self.channel)
        self._say(i18n.newParty)
        self._addPlayer(nick)
        with self.lockState:
            self.currentTimer = Timer(60, self._endWaitPeople)
            self.currentTimer.start()
            self.state = 'WAIT_PEOPLE'
