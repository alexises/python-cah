from pythonCah.security import AuthenticationManager


def test_basicAcl():
    a = AuthenticationManager()
    a.addAcl('ROLE_1')
    assert a.getRole('irc.iiens.net', '#cahBot', 'alexises', '~') == ['ROLE_1']

    a.addAcl('ROLE_2')
    assert 'ROLE_2' in a.getRole('irc.iiens.net', '#cahBot', 'alexises', '~')


def test_nonMatchingAcl():
    a = AuthenticationManager()
    a.addAcl('ROLE_1', server='irc.iiens.net')
    assert a.getRole('irc.iiens.net', '#cahBot', 'alexises', '~') == ['ROLE_1']
    assert a.getRole('notAserver', '#cahBot', 'alexises', '~') == []

    b = AuthenticationManager()
    b.addAcl('ROLE_1', channel='#cahBot')
    assert b.getRole('irc.iiens.net', '#cahBot', 'alexises', '~') == ['ROLE_1']
    assert b.getRole('irc.iiens.net', 'notAServer', 'alexises', '~') == []

    c = AuthenticationManager()
    c.addAcl('ROLE_1', nick='alexises')
    assert c.getRole('irc.iiens.net', '#cahBot', 'alexises', '~') == ['ROLE_1']
    assert c.getRole('irc.iiens.net', '#cahBot', 'notANick', '~') == []

    d = AuthenticationManager()
    d.addAcl('ROLE_1', ircRole='~')
    assert d.getRole('irc.iiens.net', '#cahBot', 'alexises', '~') == ['ROLE_1']
    assert d.getRole('irc.iiens.net', '#cahBot', 'alexises', '') == []
