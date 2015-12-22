import logging
from pythonCah.irc.authentication import SaslCapableClient
logger = logging.getLogger(__name__)

VOICE = '+'
OP = '@'
HOP = '%'
FOUNDER = '~'
ADMIN = '&'
ALL_ROLE = [VOICE, OP, HOP, FOUNDER, ADMIN]
ROLE_MAPPING = {'o': OP, 'v': VOICE, 'h': HOP, 'F': FOUNDER, 'a': ADMIN}


class UserList(object):
    def __init__(self):
        self._channel = {}

    def joinUser(self, channel, nick, mode):
        if channel not in self._channel:
            self._channel[channel] = {}
        self._channel[channel][nick] = mode

    def getUserMode(self, channel, nick):
        if channel not in self._channel:
            return ''
        if nick not in self._channel[channel]:
            return ''
        return self._channel[channel][nick]

    def partUser(self, channel, nick):
        if channel not in self._channel:
            return
        if nick not in self._channel[channel]:
            return
        del self._channel[channel][nick]

    def mode(self, channel, nick, mode):
        if channel not in self._channel:
            return
        if nick not in self._channel[channel]:
            return

        modifier = mode[0]
        modeItem = mode[1]
        if modeItem not in ROLE_MAPPING:
            return

        if modifier == '+':
            self._channel[channel][nick] = ROLE_MAPPING[modeItem]
        elif modifier == '-':
            self._channel[channel][nick] = '' 

    def listLog(self, channel):
        logger.debug('list for {}'.format(channel))
        for nick, mode in self._channel[channel].items():
             logger.debug('{}{}'.format(mode, nick))


class AutoJoinIrcClient(SaslCapableClient):
    def __init__(self, *args, **kargs):
        super(AutoJoinIrcClient, self).__init__(*args, **kargs)
        self.userList = UserList()
        self._events['376'].append(self._autoJoin)
        self._events['353'] = self._addUser
        self._events['JOIN'] = self._userJoin
        self._events['PART'] = self._userPart
        self._events['MODE'] = self._userMode
        self._events['KICK'] = self._kick
        self._channels = []

    def _addUser(self, cmd, server, args):
        channel = args[-2]
        for nick in args[-1].split(' '):
            if len(nick) < 1:
               continue
            if nick[0] in ALL_ROLE:
                role = nick[0]
                nick = nick[1:]
            else:
                role = ''
            logger.debug('add nick : {} {}'.format(nick, role))
            self.userList.joinUser(channel, nick, role)

    def _userJoin(self, cmd, server, param):
        channel = param[0]
        nick = server.split('!')[0]
        self.userList.joinUser(channel, nick, '')

    def _kick(self, cmd, server, param):
        channel = param[0]
        nick = param[1]
        self.userList.partUser(channel, nick)

    def _userPart(self, cmd, server, param):
        channel = param[0]
        nick = server.split('!')[0]
        self.userList.partUser(channel, nick)

    def _userMode(self, cmd, server, param):
        try:
            channel = param[0]
            if channel[0] != '#':
                return
            mode = param[1]
            if mode[0] not in ['+', '-']:
                return
            nick = param[2]
            self.userList.mode(channel, nick, mode)
        except IndexError:
            pass
        
    def addChannel(self, channel):
        if channel[0] != '#':
            raise ValueError('not a valid irc channel')
        self._channels.append(channel)

    def join(self, channel):
        if channel[0] != '#' and channel[0] != '&':
            logger.error('not a valid channel, skip')
        else:
            self.sendCmd('JOIN', channel)

    def _autoJoin(self, cmd, server, param):
        for i in self._channels:
            self.join(i)
