class CahBot(SingleServerIRCBot):
    def __init__(self, channel, nick, ctcp, server, dispatcher, port, ssl, sslCheck):
        SingleServerIRCBot.__init__(self, [(server, port)], nick, ctcp)
        self.ctcp = ctcp
        self.channel = channel
        self.ssl = ssl
        self.sslCheck = sslCheck
        self.dispatcher = dispatcher

    def _connect(self):
        password = None
        if len(self.server_list[0]) > 2:
            password = self.server_list[0][2]
        self.connect(self.server_list[0][0],
                     self.server_list[0][1],
                     self._nickname,
                     password,
                     ircname=self._realname,
                     ssl=self.ssl)

    def on_nicknameinuse(self, c, e):
        logger.warning('nick already in use, try another')
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        logger.info('welcome ok : join chan')
        logger.debug('join chan : ' + self.channel)
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.on_pubmsg(c, e)

    def on_pubmsg(self, c, e):
        printEntry(e)
        msg = e.arguments()[0]
        token = msg[0]
        chan = e.target()
        user = e.source().split('!')[0]
        if chan[0] != '#':
            chan = ''
        logger.debug('new msg')
        if token != self.token:
            logger.debug('not a command, avoid')
            return
        #filter empty component, like have two space
        #between cmd arguments
        cmdComponents = filter(None, msg[1:].split(' '))
        if len(cmdComponents) < 1:
            logger.debug('only a token')
            return
        cmd = cmdComponents[0]
        self.dispatcher.dispatch(c, chan, user, cmd, cmdComponents[1:])

    def get_version(self):
        return self.ctcp


