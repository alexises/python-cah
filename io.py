import logging
import socket
import ssl
import select
import re
from pprint import pformat
from threading import Thread
from Queue import Queue
logger = logging.getLogger(__name__)

class Event(object):
    def __init__(self):
        self.handlers = []
    
    def add(self, handler):
        self.handlers.append(handler)
        return self
    
    def remove(self, handler):
        self.handlers.remove(handler)
        return self
    
    def fire(self, sender, earg=None):
        for handler in self.handlers:
            handler(sender, earg)
    
    __iadd__ = add
    __isub__ = remove
    __call__ = fire


IRC_MSG_SIZE = 512
#as python-ircclient, some server seen to not folow
#the IRC rfc and end message only with line field
#or carrage return
_messageDelimiter = re.compile("\r|\n|\r\n")
class IrcClient(object):
    def __init__(self, server, port, nick, ctcp, ident='', realname='', ssl=False, sslCheck=True):
        self.server = server
        self.port = port
        self.nick = nick
        self.ssl = ssl
        self.sslCheck = sslCheck
        self.ident = ident
        self.realname = realname
        self.ctcp = ctcp
        if ident == '':
           self.ident = self.nick
        if realname == '':
           self.realname = self.ctcp
           
        self._buffer = ''
        self._events = {}
        self._events['PING'] = self._pong
        #end of motd

    def _bindSSL(self):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        #set strict security option
        ctx.set_ciphers('DH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS')
        ctx.options &= ssl.OP_NO_COMPRESSION
        if self.sslCheck:
            logger.debug('ssl check required')
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_default_certs()
            ctx.check_hostname = True
        else:
            logger.debug('no certificate check')
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        self._socket = ctx.wrap_socket(self._socket, 
                                       server_hostname=self.server)

    def connect(self):
        for res in socket.getaddrinfo(self.server, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self._socket = socket.socket(af, socktype, proto)
                break
            except socket.error as msg:
                self._socket = None
        if self.ssl:
            self._bindSSL()
        self._socket.connect(sa)
        logger.debug('we have connectioon, begin loop')
        self._initialCmd()
        if self.ssl:
            version = self._socket.version()
            logger.info('ssl version : {}'.format(version))
            cipher = self._socket.cipher()
            logger.info('cipher : {}'.format(cipher))
            cert = self._socket.getpeercert()
            logger.info('provided certificate {}'.format(pformat(cert)))
        self._eventLoop()

    def _initialCmd(self):
        self.sendCmd('NICK', self.nick)
        self.sendCmd('USER', '{0} {1} {1} :{2}'.format(self.nick, self.server, self.realname))

    def notice(self, dest, message):
        self.sendCmd('NOTICE', dest + ' :' + message)
   
    def privmsg(self, dest, message):
        self.sendCmd('PRIVMSG', dest + ' :' + message)

    def sendCmd(self, cmd, args):
        msg = cmd + ' ' + args + '\r\n'
        if len(msg) > IRC_MSG_SIZE:
            raise ValueError('msg max size is {}, current message have {} size'.format(IRC_MSG_SIZE, len(msg)))

        logger.debug(msg)
        self._socket.sendall(msg)

    def _computeMsg(self, msg):
        logger.debug(msg)

        server = ''
        if msg[0] == ':':
            server = msg[1:].split(' ')[0]
            msg = msg[2+len(server):]
        component = msg.split(':')
        longParam = ':'.join(component[1:])
        param = filter(len, component[0].split(' '))
        cmd = param[0]
        param = param[1:] + [longParam]
        logger.debug("server '{}' cmd '{}' param '{}'".format(server, cmd, param)) 
       
        try:
            for cmd in self._events[cmd]:
                cmd(cmd, server, param)
        except TypeError:
            self._events[cmd](cmd, server, param)
        except KeyError:
            #no event, just skip it
            pass

    def _pong(self, cmd, server, param):
        self.sendCmd('PONG', param[0])

    def _eventLoop(self):
        while 1:
            select.select([self._socket], [], [])
            data = self._socket.recv(4*IRC_MSG_SIZE)
            lines = _messageDelimiter.split(self._buffer + data)
            
            self._buffer = lines.pop()
            for msg in lines:
                if msg == '':
                    #due to regexp biavior, we can have empty line
                    continue
                self._computeMsg(msg)

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
                 if self._capabilityEvent.has_key(capability):
                     self._capabilityEvent[capability]
         #end of capability negociation
         self.sendCmd('CAP', 'END')

VOICE = '+'             
OP = '@'
HOP = '%'
FOUNDER = '~'
ADMIN = '&'
ALL_ROLE = [VOICE, OP, HOP, FOUNDER, ADMIN]
ROLE_MAPPING = { 'o' : OP, 'v' : VOICE, 'h' : HOP, 'F' : FOUNDER, 'a' : ADMIN }
class UserList(object):
    def __init__(self):
        self._channel = {}

    def joinUser(self, channel, nick, mode):
        if not self._channel.has_key(channel):
            self._channel[channel] = {}
        self._channel[channel][nick] = mode

    def getUserMode(self, channel, nick):
        if not self._channel.has_key(channel):
            return ''
        if not self._channel[channel].has_key(nick):
            return ''
        return self._channel[channel][nick]

    def partUser(self, channel, nick):
        if not self._channel.has_key(channel):
            return
        if not self._channel[channel].has_key(nick):
            return
        del self._channel[channel][nick]

    def mode(self, channel, nick, mode):
        if not self._channel.has_key(channel):
            return
        if not self._channel[channel].has_key(nick):
            return

        modifier = mode[0]
        modeItem = mode[1]
        if not ROLE_MAPPING.has_key(modeItem):
            return

        if modifier == '+':
            self._channel[channel][nick] = ROLE_MAPPING[modeItem]
        elif modifier == '-':
            self._channel[channel][nick] = '' 

    def listLog(self, channel):
        logger.debug('list for {}'.format(channel))
        for nick, mode in self._channel[channel].iteritems():
             logger.debug('{}{}'.format(mode, nick))

class AutoJoinIrcClient(IRCCapabilityNegociationIrcClient):
    def __init__(self, server, port, nick, ctcp, ident=None, realname=None, ssl=False, sslCheck=True):
        super(AutoJoinIrcClient, self).__init__(server, port, nick, ctcp, ident, realname, ssl, sslCheck)
        self.userList = UserList()
        self._events['376'] = self._autoJoin
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


class NonBlockingIrcClient(AutoJoinIrcClient):
    def __init__(self, server, port, nick, ctcp, ident=None, realname=None, ssl=False, sslCheck=True):
        super(NonBlockingIrcClient, self).__init__(server, port, nick, ctcp, ident, realname, ssl, sslCheck)
        self._thread = Thread(target = self.connect )
        self._thread.daemon = True

    def start(self):
        self._thread.start()

class IrcClientNode(NonBlockingIrcClient):
    def __init__(self, queue, server, port, nick, ctcp, ident=None, realname=None, ssl=False, sslCheck=True):
        super(IrcClientNode, self).__init__(server, port, nick, ctcp, ident, realname, ssl, sslCheck)
        self._queue = queue
        self._events['PRIVMSG'] = self._passEventInQueue
        self._events['NOTICE'] = self._passEventInQueue

    def _passEventInQueue(self, cmd, sender, param):
        self._queue.put((self, cmd, sender, param))
    
class MultiIrcClient(object):
    def __init__(self, servers):
        self._servers = []
        self._queue = Queue()
        for server in servers:
            channels = server['channels']
            del server['channels']
            client = IrcClientNode(self._queue, **server)
            self._servers.append(client)
            for i in channels:
                client.addChannel(i)
            
        self.command = {}
        self.command['NOTICE'] = self.notice
        self.command['PRIVMSG'] = self.privmsg

    def privmsg(self, server, sender, destination, message):
        logger.debug('privmsg')
        pass
    
    def notice(self, server, sender, destination, message):
        logger.debug('notice')
        pass

    def start(self):
        for server in self._servers:
            server.start()

        while 1:
            server, cmd, sender, param = self._queue.get()
            if cmd == 'PRIVMSG' or cmd == 'NOTICE':
                destination = param[0]
                message = param[1]
            self.command[cmd](server, sender, destination, message)
