from pythonCah.config import loadConfig
import pytest


def test_errorJson():
    with pytest.raises(ValueError):
        loadConfig('jdt/errorJson.json')


def test_unavailableFile():
    with pytest.raises(FileNotFoundError):
        loadConfig('jdt/notAFile.json')


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
