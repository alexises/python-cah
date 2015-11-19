import logging
import string
from game import CAHGame
logger = logging.getLogger(__name__)

class CmdDispatch(object):
      def __init__(self):
          logger.debug('init CmdDispatch')
          self.cmd = {}
          self.party = {}
          self.appendCmd('log', self.logCmd)
          self.appendCmd('start', self.startCmd)
          self.appendCmd('notice', self.noticeCmd)

      def appendCmd(self, cmdName, callback):
          self.cmd[cmdName] = callback

      def dispatch(self, serverData, channel, user, command, args): 
          logger.debug('dispach command : ' + command)
          if not self.cmd.has_key(command):
              logger.warning('unknow command, skip it')
              return
          callback = self.cmd[command]
          callback(serverData, channel, user, args)

      def logCmd(self, serverData, channel, user, args):
          logger.info('LOG '+ str(args))

      def noticeCmd(self, serverData, channel, user, args):
          logger.info('NOTICE '+ str(args))
          serverData.notice(args[0], string.join(args[1:], ' '))

      def startCmd(self, serverData, channel, user, args):
          if self.party.has_key(channel):
              logger.error('party already running, forbid command')
              return
          logger.info('start a new game under ' +  channel)
          game = CAHGame(self, channel, serverData)
          game.start(user)
          self.party[channel] = game
