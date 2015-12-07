import logging
'''Security provides way to manage secured command'''

logger = logging.getLogger(__name__)

def authentication_from_config(authentication, authorization):
    """ create authentication manager instance from two list of dict 
        authentication : provides roles based on irc attribute
        authorization : provides allowed command from role
    """
    auth = AuthenticationManager()
    for acl in authentication:
        auth.addAcl(**acl)
    author = AuthorizationManager(auth)
    for acl in authorization:
        author.add(**acl)

    return author

class AuthenticationManager(object):
    ALL_SERVER = ''
    ALL_CHANNEL = ''
    ALL_NICK = ''
    NO_ROLE = ''
    VOICE = '+'
    OP = '@'
    HOP = '%'
    ADMIN = '&'
    FOUNDER = '~'
    def __init__(self):
        self.acl = []

    def addAcl(self, role, server=ALL_SERVER, channel=ALL_CHANNEL, 
               nick=ALL_NICK, ircRole=NO_ROLE):
        logger.debug('add acl {} {} {} {} {}'.format(server, channel, nick, ircRole, role))
        acl = (server, channel, nick, ircRole, role)
        self.acl.append(acl)

    def getRole(self, server, channel, nick, ircRole):
        groups = []
        for iserver, ichannel, inick, iircRole, iappRole in self.acl:
            if server != iserver and iserver != self.ALL_SERVER:
                continue
            if channel != ichannel and ichannel != self.ALL_CHANNEL:
                continue
            if nick != inick and inick != self.ALL_NICK:
                continue
            if ircRole != iircRole and iircRole != self.NO_ROLE:
                continue
            logger.info('mached acl {} {} {} {} {}'.format(iserver, ichannel, inick, iircRole, iappRole))
            groups.append(iappRole)
        logger.debug('all group : {}'.format(groups))
        return list(set(groups))

class AuthorizationManager(object):
    def __init__(self, authenticationManager):
        self.acl = {}
        self.authenticationManager = authenticationManager
   
    def add(self, command, role):
        logger.debug('add acl {} {}'.format(command, role)) 
        if not self.acl.has_key(command):
            self.acl[command] = []
        self.acl[command].append(role)

    def authenticate(self, server, channel, nick, ircRole, command):
        roles = self.authenticationManager.getRole(server, channel, nick, ircRole)
        neededRole = self.acl[command]
        logger.debug('neededRole : {}'.format(neededRole))
        logger.debug('roles : {}'.format(roles))
        if neededRole == [] or neededRole == None:
            return True
        matchedRole = list(set(roles).intersection(neededRole))
        if matchedRole == []:
            return False
        return True
