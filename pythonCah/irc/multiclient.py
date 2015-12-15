import logging
from pythonCah.irc.channelInfo import AutoJoinIrcClient
import logging
from threading import Thread
from queue import Queue
logger = logging.getLogger(__name__)

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

    def _handleSignal(self):
        self._queue.put(('', 'EXCEPT', '', []))

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
            if cmd == 'EXCEPT':
                raise KeyboardInterrupt()
            if cmd == 'PRIVMSG' or cmd == 'NOTICE':
                destination = param[0]
                message = param[1]
            self.command[cmd](server, sender, destination, message)
