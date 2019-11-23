import pytest
from os import environ, remove, makedirs, strerror, getcwd
import random
import string
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

STDOPTIONSWKEY = dict(STDOPTIONS)
STDOPTIONSWKEY.update({'apikey':APIKEY})

def fixdirectory(options,tmpdir):
    path = str(tmpdir.dirpath()) + '/'
    options.update({'directory':path})

def test_noargs():
    with pytest.raises(RuntimeError):
        testobj = organizer.Organizer({})

def test_createobjwithkey(tmpdir):
    fixdirectory(STDOPTIONSWKEY, tmpdir)
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


def test_goodapikeyfile(tmpdir):
    keyfile = getcwd() + '/apikey.ini'
    f = open(keyfile, 'w')
    f.write("TMDB_API_KEY = '"+APIKEY+"'\n")
    f.close()

    fixdirectory(STDOPTIONS, tmpdir)
    testobj = organizer.Organizer(STDOPTIONS)

    assert testobj.apikey == APIKEY

    remove(keyfile)

def test_destination(tmpdir):
    testoptions = dict(STDOPTIONSWKEY)
    path = str(tmpdir.dirpath())+'/'
    testoptions.update({'directory':path})
    testobj = organizer.Organizer(testoptions)

    assert testobj.optionsdict['destination'] == path

def test_baddestination():
    letters = string.ascii_lowercase
    randomFolderName = ''.join(random.choice(letters) for i in range(20))

    baddir = '/tmp/'+randomFolderName+'/'

    testoptions = dict(STDOPTIONSWKEY)
    testoptions.update({'destination':baddir})

    with pytest.raises(FileNotFoundError):
        testobj = organizer.Organizer(testoptions)

def test_createslash(tmpdir):
    pathnoslash = str(tmpdir.dirpath())
    testoptions = dict(STDOPTIONSWKEY)
    testoptions.update({'directory': pathnoslash})
    testobj = organizer.Organizer(testoptions)

    assert testobj.optionsdict['directory'] == pathnoslash+'/'