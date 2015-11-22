import logging
'''Security provides way to manage secured command'''

logger = logging.getLogger(__name__)

class AuthenticationManager(self):
    ALL_SERVER = ''
    ALL_CHANNEL = ''
    ALL_NICK = ''
    NO_ROLE = ''
    VOICE = '+'
    OP = '@'
    HOP = '&'
    FOUNDER = '~'
    def __init__(self):
        self.acl = []

    def addAcl(self, server=ALL_SERVER, channel=ALL_CHANNEL, 
               nick=ALL_NICK, ircRole=NO_ROLE, appRole):
        logger.debug('add acl {} {} {} {} {}'.format(server, channel, nick, ircRole, appRole))
        acl = (server, channel, nick, ircRole, appRole)
        self.acl.append(acl)

    def getRole(self, server, channel, nick, ircRole):
        groups = []
        for iserver, ichannel, inick, iircRole, iappRole in self.acl:
            if serer != iserver and iserver != ALL_SERVER:
                continue
            if channel != ichannel and ichannel != ALL_CHANNEL:
                continue
            if nick != inick and inick != ALL_NICK:
                continue
            if ircRole != iircRole and irole != NO_ROLE:
                continue
            logger.info('mached acl {} {} {} {} {}'.format(iserver, ichannel, inick, iircRole, iappRole))
            groups.extend(iappRole)
        return list(set(groups))

class AuthorizartionManager(self)
    def __init__(self, authenticationManager):
        self.acl = {}
        self.authenticationManager = authenticationManager
   
    def add(self, comamnd, role):
        logger.debug('add acl {} {}'.format(command, role)) 
        if self.acl[command] == None:
            self.acl[command] = []
        self.acl[command].append(role)

    def authenticate(self, server, channel, nick, ircRole, command)
        roles = self.authenticationManager.getRole(server, channel, nick, ircRole)
        neededRole = self.acl[command]
        if neededRole == [] or neededRole == None:
            return True
        matchedRole = list(set(roles).intersection(neededRole))
        if matchedROle == []:
            return False
        return True
