import logging
import string
from .game import CAHGame
from .cards import MultiStack, BlackCardStack, WhiteCardStack
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
        if command not in self.cmd:
            logger.warning('unknow command, skip it')
            return
        role = serverData.userList.getUserMode(channel, user)
        logger.debug('irc role : "{}"'.format(role))
        if not self.security.authenticate(
            serverData.server, channel, user, role, command):
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
        self.appendCmd('stop', self.stopCmd)
 
    def logCmd(self, serverData, channel, user, args):
        logger.info('LOG '+ str(args))

    def noticeCmd(self, serverData, channel, user, args):
        logger.info('NOTICE '+ str(args))
        serverData.notice(args[0], string.join(args[1:], ' '))

    def listCmd(self, serverData, channel, user, args):
        serverData.userList.listLog(channel)

    def startCmd(self, serverData, channel, user, args):
        if channel in self.party:
            logger.error('party already running, forbid command')
            return False
        logger.info('start a new game under ' +  channel)
        game = CAHGame(self, channel, serverData, self.blackDeck, self.whiteDeck)
        game.start(user)
        self.party[channel] = game
        return True

    def stopCmd(self, serverData, channel, user, args):
        if channel not in self.party:
            logger.error("no party is running, silent ignore")
            return False
        party = self.party[channel]
        party._say('stop requested, print score and exit')
        party.scoreCmd(serverData, channel, user, args)
        del self.party[channel]
        del party
        return True


class AutoVoiceDispatch(BaseGameDispatch):
    def __init__(self, *args, **kargs):
        super(AutoVoiceDispatch, self).__init__(*args, **kargs)
        self._autoVoice = {}
 
    def startCmd(self, serverData, channel, user, args):
        result = super(AutoVoiceDispatch, self).startCmd(serverData, channel, user, args)
        if not result:
            return
        mode = serverData.userList.getUserMode(channel, user)
        if mode not in ['', ' ']:
            #user already privilegied, skip
            return
        self._autoVoice[channel] = user
        serverData.mode(channel, '+v', user)

    def stopCmd(self, serverData, channel, user, args):
        result = super(AutoVoiceDispatch, self).stopCmd(serverData, channel, user, args)
        if not result:
            return
        if channel not in self._autoVoice:
            return
        logger.debug('remove role')
        serverData.mode(channel, '-v', self._autoVoice[channel])
        del self._autoVoice[channel]


class InpersonateServerContainer(object):
    def __init__(self, serverData, channel, user):
        self.serverData = serverData
        self.channel = channel
        self.user = user
    
    def _getDestination(self, dest):
        if dest[0] in ['&', '#']:
            return dest
        return self.user

    def notice(self, dest, data):
        realDest = self._getDestination(dest)
        self.serverData.notice(realDest, data)

    def privmsg(self, dest, data):
        realDest = self._getDestination(dest)
        self.serverData.privmsg(realDest, data)

    def __getattr__(self, name):
        return getattr(self.serverData, name)

class InpersonateDispatch(AutoVoiceDispatch):
    def __init__(self, *args, **kargs):
        super(InpersonateDispatch, self).__init__(*args, **kargs)
        self.appendCmd('inpersonate', self.inpersonateCmd)

    def inpersonateCmd(self, serverData, channel, user, args):
        inpersonateServerData = InpersonateServerContainer(serverData, channel, user)
        user = args.pop(0)
        command = args.pop(0)
        self.dispatch(inpersonateServerData, channel, user, command, args)
