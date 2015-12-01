""" configuration for the bot """
from marshmallow import Schema, fields, validate, post_load
from pprint import pprint
import json
import logging

logger = logging.getLogger(__name__)
ircNickRegexp = r'([a-zA-Z][a-zA-Z0-9\[\]\\\{\}\^-]{0,15})?'
channelRegexp = r'#' + ircNickRegexp

class Channel(object):
    def __init__(self, data):
        self.__dict__.update(data)

class Server(object):
    def __init__(self, data):
        self.__dict__.update(data)
        self.channels = []
        for i in data['channels']:
            self.channels.append(Channel(i))

    def propagateDefaultValue(self):
        for channel in self.channels:
            self._setDefaultChannelValue(channel)

    def _setDefaultChannelValue(self, channel):
        if channel.token == '':
            channel.token = self.token
        if channel.startTimeout == 0:
            channel.startTimeout == self.startTimeout
        if channel.pickTimeout == 0:
            channel.pickTimeout == self.pickTimeout

    def __getitem__(self, key):
        for i in self.channels:
            if i.channel == key:
                return i
        channel = Channel({ 'token' : '', 'startTimeout' : 0 , 'pickTimeout' : 0})
        self._setDefaultChannelValue(channel)
        return channel
        
    def getBasicParams(self):
        params = {}
        params['server'] = self.server
        params['port'] = self.port
        params['nick'] = self.nick
        params['ident'] = self.ident
        params['ctcp'] = self.ctcp
        params['realname'] = self.realname
        params['ssl'] = self.ssl
        params['sslCheck'] = self.sslCheck
        params['channels'] = []
        for i in self.channels:
            params['channels'].append(i.channel)

        logger.debug('params : {}'.format(params))
        return params

class Config(object):
    def __init__(self, data):
        print data
        self.__dict__.update(data)
        self.servers = []
        for i in data['servers']:
            self.servers.append(Server(i))
        self.propagateDefaultValue()

    def propagateDefaultValue(self):
        for server in self.servers:
            if server.token == '':
                server.token = self.token
            if server.startTimeout == 0:
                server.startTimeout = self.startTimeout
            if server.pickTimeout == 0:
                server.pickTimeout = self.pickTimeout
            if server.ctcp == '':
                server.ctcp = self.ctcp
            if server.nick == '':
                server.nick = self.nick
            server.propagateDefaultValue()

    def serverList(self):
        servers = []
        for server in self.servers:
            servers.append(server.getBasicParams())
        return servers

    def __getitem__(self, key):
        server = key.server
        port = key.port

        for i in self.servers:
            if i.port == port and i.server == server:
                return i

class ChannelSchema(Schema):
    channel = fields.Str(required = True, validate = validate.Regexp(channelRegexp))
    token = fields.Str(missing = ' ', validate=validate.Length(min = 1, max = 1))
    startTimeout = fields.Integer(missing = 0, validate = validate.Range(min = 0, max = 300))
    pickTimeout = fields.Integer(missing = 0, validate = validate.Range(min = 0, max = 300))


class ServerSchema(Schema):
    server = fields.Str(required=True)
    port = fields.Integer(missing=6667, validate = validate.Range(min = 1, max = 65535))
    token = fields.Str(missing=' ', validate = validate.Length(min = 1, max = 1))
    startTimeout = fields.Integer(missing = 0, validate = validate.Range(min = 0, max = 300))
    pickTimeout = fields.Integer(missing = 0, validate = validate.Range(min = 0, max = 300))
    nick = fields.Str(missing = '', validate = validate.Regexp(ircNickRegexp))
    ident = fields.Str(missing = '')
    realname = fields.Str(missing  = '')
    ctcp = fields.Str(missing = '')
    ssl = fields.Boolean(missing = False)
    sslCheck = fields.Boolean(missing = True)
    channels = fields.Nested(ChannelSchema, required = True, many = True)

class ConfigSchema(Schema):
    ctcp = fields.Str(missing = "python-cah")
    nick = fields.Str(required = True, validate = validate.Regexp(ircNickRegexp))
    ident = fields.Str(missing = '')
    realname = fields.Str(missing  = '')
    token = fields.Str(missing = '!', validate = validate.Length(min = 1, max = 1))
    startTimeout = fields.Integer(missing = 60, validate = validate.Range(min = 1, max = 300))
    pickTimeout = fields.Integer(missing = 60, validate = validate.Range(min = 1, max = 300))
    servers = fields.Nested(ServerSchema, required = True, many = True)

    @post_load
    def hydrate(self, data):
        return Config(data)

def loadConfig(filename):
    with open(filename) as fd:
        data = json.load(fd)
    schema = ConfigSchema(many = False)
    result = schema.load(data)
    if len(result.errors) > 1:
        raise ValueError(result.errors)
    return result.data 
