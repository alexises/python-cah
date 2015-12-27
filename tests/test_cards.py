import pytest
from pythonCah.cards import WhiteCardStack


def test_errorJson():
    with pytest.raises(ValueError):
        WhiteCardStack('jdt/errorJson.json')


def test_unavailableFile():
    with pytest.raises(FileNotFoundError):
        WhiteCardStack('jdt/notAFile.json')


def test_basicWhiteStack():
    s = WhiteCardStack('jdt/twoWhiteCard.json')
    assert len(s) == 2

    a = s.pick()
    b = s.pick()
    assert a != b
    c = s.pick()
    assert c in [a, b]
