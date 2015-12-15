import logging
from pythonCah.irc.network import IrcClient
logger = logging.getLogger(__name__)


class IRCCapabilityNegociationIrcClient(IrcClient):
     def __init__(self, *param):
         super(IRCCapabilityNegociationIrcClient, self).__init__(*param)
         self._capabilityEvent = {}
         self._events['CAP'] = self._capNegociation
         self._capabilities = []

     def _initialCmd(self):
         self.sendCmd('CAP', 'LS')
         super(IRCCapabilityNegociationIrcClient, self)._initialCmd()

     def _capNegociation(self, cmd, server, param):
         try:
             cmd = param[1]
             capList = param[2]     
         except IndexError:
             pass
         else:
             logger.info('capability list ok')
             for capability in capList.split(' '):
                 logger.debug('add capability : ' + capability)
                 if capability == '':
                     continue
                 self._capabilities.append(capability)
                 if capability in self._capabilityEvent:
                     self._capabilityEvent[capability]
         #end of capability negociation
         self.sendCmd('CAP', 'END')
