from pythonCah.config import loadConfig
from pythonCah.security import AuthenticationManager as AM
from marshmallow.exceptions import ValidationError
import pytest


def test_errorJson():
    with pytest.raises(ValueError):
        loadConfig('jdt/errorJson.json')


def test_unavailableFile():
    with pytest.raises(FileNotFoundError):
        loadConfig('jdt/notAFile.json')


def test_errorConfig():
    with pytest.raises(ValidationError):
        loadConfig('jdt/configError.json')


def test_minimalConfig():
    c = loadConfig('jdt/minimalConfig.json')
    serverlist = c.serverList()
    assert len(serverlist) == 1
    params = serverlist[0]
    assert params['server'] == 'irc.iiens.net'
    assert params['port'] == 7000
    assert params['nick'] == 'nono-devel'
    assert params['ctcp'] == "I'm a dunny bot under devel"
    assert params['realname'] == ''
    assert params['ssl'] is False
    assert params['sslCheck'] is True
    assert params['withSasl'] is False
    assert params['password'] == ''
    assert len(params['channels']) == 1
    channel = params['channels'][0]
    assert channel == '#cahbot2'


def test_channelDefaultValuePropagate():
    c = loadConfig('jdt/minimalConfig.json')
    server = c.servers[0]
    channel = server.channels[0]
    assert len(server.channels) == 1
    assert channel.token == '!'
    assert c.startTimeout == 60
    assert c.pickTimeout == 60
    assert server.startTimeout == 60
    assert server.pickTimeout == 60
    assert channel.startTimeout == 60
    assert channel.pickTimeout == 60
    assert channel.autoVoice is False


def test_override():
    c = loadConfig('jdt/override.json')
    server = c.servers[0]
    channel = server.channels[0]
    assert c.startTimeout == 10
    assert c.pickTimeout == 10
    assert c.token == '$'
    assert c.autoVoice is True
    assert server.startTimeout == 20
    assert server.pickTimeout == 20
    assert server.token == '%'
    assert server.autoVoice is False
    assert channel.startTimeout == 30
    assert channel.pickTimeout == 30
    assert channel.token == ','
    assert channel.autoVoice is True


def test_aclMinimal():
    c = loadConfig('jdt/minimalConfig.json')
    assert len(c.acl) == 8
    acl1 = c.acl[0]
    assert acl1['role'] == 'ROLE_PLAYER'
    assert acl1['server'] == AM.ALL_SERVER
    assert acl1['ircRole'] == AM.NO_ROLE
    assert acl1['channel'] == AM.ALL_CHANNEL
    assert acl1['nick'] == AM.ALL_NICK


def test_aclOverride():
    c = loadConfig('jdt/minimalConfig.json')
    acl1 = c.acl[1]
    assert acl1['role'] == 'ROLE_DEBUG'
    assert acl1['server'] == 'irc.iiens.net'
    assert acl1['ircRole'] == '~'
    assert acl1['channel'] == '#cahBot'
    assert acl1['nick'] == 'alexises'


def test_roleMapping():
    c = loadConfig('jdt/minimalConfig.json')
    roles = c.roleMapping
    assert len(roles) == 9
    assert roles[0]['command'] == 'log'
    assert roles[0]['role'] == 'ROLE_DEBUG'
    assert roles[8]['command'] == 'inpersonate'
    assert roles[8]['role'] == 'ROLE_INPERSONATE'


class ConfigWrapper(object):
    def __init__(self, server, port):
        self.server = server
        self.port = port


def test_getConfig():
    c = loadConfig('jdt/minimalConfig.json')
    s1 = c[ConfigWrapper('irc.iiens.net', 7000)]
    assert s1.server == 'irc.iiens.net'

    s2 = c[ConfigWrapper('notExist', 65535)]
    assert s2 is None

    ch1 = s1['#cahbot2']
    assert ch1.channel == '#cahbot2'
    ch2 = s1['#notExitst']
    assert not hasattr(ch2, 'channel')
