import logging
import string
from game import CAHGame
from cards import MultiStack, BlackCardStack, WhiteCardStack
logger = logging.getLogger(__name__)

class CmdDispatch(object):
    def __init__(self, security):
        logger.debug('init CmdDispatch')
        self.security = security
        self.cmd = {}

    def appendCmd(self, cmdName, callback):
        self.cmd[cmdName] = callback

    def dispatch(self, serverData, channel, user, command, args):
        logger.debug('dispach command : ' + command)
        if not self.cmd.has_key(command):
            logger.warning('unknow command, skip it')
            return
        role = serverData.userList.getUserMode(channel, user)
        logger.debug('irc role : "{}"'.format(role))
        if not self.security.authenticate(serverData.server, channel, user, role, command):
            logger.warning('no permission allowed to execute this command, skip')
            return
        callback = self.cmd[command]
        callback(serverData, channel, user, args)

class BaseGameDispatch(CmdDispatch):
    def __init__(self, blackDeckFiles, whiteDeckFiles, security):
        super(BaseGameDispatch, self).__init__(security) 
        self.party = {}
        self.whiteDeck = MultiStack()
        self.blackDeck = MultiStack()
        self.whiteDeck.addFiles(whiteDeckFiles, WhiteCardStack)
        self.blackDeck.addFiles(blackDeckFiles, BlackCardStack)
        self.appendCmd('log', self.logCmd)
        self.appendCmd('start', self.startCmd)
        self.appendCmd('notice', self.noticeCmd)
        self.appendCmd('list', self.listCmd)
 
    def logCmd(self, serverData, channel, user, args):
        logger.info('LOG '+ str(args))

    def noticeCmd(self, serverData, channel, user, args):
        logger.info('NOTICE '+ str(args))
        serverData.notice(args[0], string.join(args[1:], ' '))

    def listCmd(self, serverData, channel, user, args):
        serverData.userList.listLog(channel)

    def startCmd(self, serverData, channel, user, args):
        if self.party.has_key(channel):
            logger.error('party already running, forbid command')
            return
        logger.info('start a new game under ' +  channel)
        game = CAHGame(self, channel, serverData, self.blackDeck, self.whiteDeck)
        game.start(user)
        self.party[channel] = game
