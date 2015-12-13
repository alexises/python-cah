from pprint import pformat 
import logging
import socket
import ssl
import select
import re
logger = logging.getLogger(__name__)

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
