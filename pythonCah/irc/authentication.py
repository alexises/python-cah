from pythonCah.irc.ircv3 import IRCCapabilityNegociationIrcClient
import logging
import base64

logger = logging.getLogger(__name__)


class SaslCapableClient(IRCCapabilityNegociationIrcClient):
    def __init__(self, *args, withSasl=False, password='', **kargs):
        super(SaslCapableClient, self).__init__(*args, **kargs)
        self.password = password
        logger.debug('launch sasl capable client')
        if withSasl:
            self._capabilityEvent['sasl'] = self._negociateSasl
        elif password != '':
            self._events['376'].append(self._nickservIdent)

    def _nickservIdent(self, cmd, server, param):
        self.privmsg('NickServ', 'IDENTIFY ' + self.password)

    def _negociateSasl(self):
        self.info('initiate sasl negociation')

        self.debug('require sasl')
        self.sendCmd('CAP', 'REQ sasl')

        (cmd, server, param) = self._getCommand()
        if cmd != 'CAP' or len(param) == 0 or param[0] not in ['NAK', 'ACK']:
            self.warning("server don't proper handle capability, end")
            return
        if param[0] == 'NAK':
            self.warning('sasl capability forbiden by server, end negociation')
            return
        self.debug('sasl capability correctly negociated')

        self.sendCmd('AUTHENTICATE', 'PLAIN')
        (cmd, server, param) = self._getCommand()
        if cmd == '904':
            logger.warning('bad authentication mecanism, abord')
            self.sendCmd('AUTHENTICATE', '*')
            return
        if cmd != 'AUTHENTICATE':
            logger.critical('bad response, abord')
            self.sendCmd('AUTHENTICATE', '*')
            return

        encodedPassword = base64.b64encode(
            self.nick + "\0" + self.nick + "\0" + self.password)
        if encodedPassword > 400:
            raise NotImplemented('not able to cut password')
        logger.debug('send password')
        self.sendCmd('AUTHENTICATE', encodedPassword)

        (cmd, server, param) = self._getCommand()
        if cmd == '904' or cmd == '905':
            logger.error('bad password')
            self.sendCmd('AUTHENTICATE', '*')
            return
        if cmd == '903':
            logger.info('sasl authentication successfull')
            return
        else:
            logger.critical('bad command, skip it')
            return
