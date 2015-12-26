from pythonCah.config import loadConfig
import pytest


def test_errorJson():
    with pytest.raises(ValueError):
        loadConfig('jdt/errorJson.json')


def test_unavailableFile():
    with pytest.raises(FileNotFoundError):
        loadConfig('jdt/notAFile.json')


def test_minimalConfig():
    loadConfig('jdt/minimalConfig.json')
