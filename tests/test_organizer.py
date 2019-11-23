import pytest
from os import environ, remove, makedirs, strerror, getcwd
from pathlib import Path

from cinefolders import organizer

# def create_api_file(dir):
#     with open

APIKEY = environ['TMDB_API_KEY']

STDOPTIONS = {'copy': False,
                    'debug': True,
                    'destination': None,
                    'directory': '/tmp/videos',
                    'dry_run': False,
                    'l': False,
                    'v': False,
                    'x': None,
              }

STDOPTIONSWKEY = dict(STDOPTIONS).update({'apikey':APIKEY})

def test_createobjwithkey():
    testo = organizer.Organizer(STDOPTIONSWKEY)
    assert testo.apikey == APIKEY

def test_createobjnokey(monkeypatch):
    # monkeypatch.setattr('builtins.input', lambda: APIKEY)
    with pytest.raises(FileNotFoundError):
        testo = organizer.Organizer(STDOPTIONS)

def test_badapikeyfile():
    keyfile = getcwd() + '/apikey.ini'
    f = open(keyfile, 'w')
    f.write("TMDB_API_KEY = dasfasd\n")
    f.close()
    with pytest.raises(OSError):
        testobj = organizer.Organizer(STDOPTIONS)

    remove(keyfile)


def test_goodapikeyfile():
    keyfile = getcwd() + '/apikey.ini'
    f = open(keyfile, 'w')
    f.write("TMDB_API_KEY = '"+APIKEY+"'\n")
    f.close()

    testobj = organizer.Organizer(STDOPTIONS)

    assert testobj.apikey == APIKEY

    remove(keyfile)