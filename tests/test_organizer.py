import pytest
from os import environ, remove, makedirs, strerror, getcwd
import random
import string
from pathlib import Path
from guessit import guessit

from cinefolders import organizer

from cinefolders.tmdb import movie

# def create_api_file(dir):
#     with open

APIKEY = environ['TMDB_API_KEY']

STDOPTIONS = {  'copy': False,
                'debug': False,
                'destination': None,
                'directory': '/tmp/videos',
                'dry_run': False,
                'l': False,
                'v': False,
                'x': None,
              }

STDOPTIONSWKEY = dict(STDOPTIONS)
STDOPTIONSWKEY.update({'apikey':APIKEY})

MOVIES = ['Down Periscope_UHD_.mp4',
          'Down Periscope.avi',
          'Down Periscope directors cut 4k.avi',
          ]

MYEARS = [1996,
          1996,
          1996,
          ]

#note - these don't include the container / extension
FMNAMES =['Movies/Down Periscope (1996)/Down Periscope (1996) - Ultra HD',
          'Movies/Down Periscope (1996)/Down Periscope (1996)',
          "Movies/Down Periscope (1996)/Down Periscope (1996) - 2160p Director's Cut",
          ]

STRUCTURE = [   'Down_periscope_directors_cut_4k.avi',
                'Grand Budapest Hotel (2014).mkv',
                # 'dsfasdfd/dfasdlkjfosokij.mp4', #this is really hard to handle well it works on some environments only
                'Mulan/dswojf32908.mp4',
                'Good Ones/Horror/The.Shining.1980.US.DC.1080p.BluRay.H264.AAC-RARBG.mp4',
                'Avatar - 2x02 -.mkv'
                ]

CORRECTST = ["Movies/Down Periscope (1996)/Down Periscope (1996) - 2160p Director's Cut.avi",
             "Movies/The Grand Budapest Hotel (2014)/The Grand Budapest Hotel (2014).mkv",
             # "Movies/Dfasdlkjfosokij/Dfasdlkjfosokij.mp4",
             "Movies/Mulan (1998)/Mulan (1998).mp4",
             "Movies/The Shining (1980)/The Shining (1980) - 1080p Director's Cut.mp4",
             "TV Shows/Avatar: The Last Airbender/Season 2/Avatar: The Last Airbender S02E02 The Cave of Two Lovers.mkv"]


def fixdirectory(options,tmpdir):
    path = str(tmpdir.dirpath()) + '/'
    options.update({'directory':path})

def createdirstructure(newdir):
    for s in STRUCTURE:

        completepath = str(newdir) + '/videos/' + s
        dirs = completepath.split('/')
        justpath = '/'.join(dirs[:-1])
        # assert justpath == completepath

        try:
            Path(justpath).mkdir(parents=True)
        except FileExistsError as fee:
            if(fee.errno == 17):
                pass
            else:
                raise fee

        Path(completepath).touch()

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

    assert testobj.optionsdict['destination'] == Path(path)

def test_baddestination():
    #make sure destination is created
    letters = string.ascii_lowercase
    randomFolderName = ''.join(random.choice(letters) for i in range(20))

    baddir = '/tmp/'+randomFolderName+'/'

    testoptions = dict(STDOPTIONSWKEY)
    testoptions.update({'destination':baddir})

    # with pytest.raises(FileNotFoundError):
    testobj = organizer.Organizer(testoptions)
    assert Path(baddir).exists()

def test_namingmovies(tmpdir):
    fixdirectory(STDOPTIONSWKEY, tmpdir)
    testobj = organizer.Organizer(STDOPTIONSWKEY)

    for i in range(len(MOVIES)):
        gdict = guessit(MOVIES[i])
        testtitle = gdict['title']
        fakemovie = movie.Movie({'id':0,'title':testtitle,'release_date':str(MYEARS[i])},None)
        newPath = testobj.buildpath(fakemovie, gdict)
        assert newPath == FMNAMES[i]

def test_createdirstructure(tmpdir):
    createdirstructure(tmpdir.dirpath())
    for s in STRUCTURE:
        p = Path(str(tmpdir.dirpath())+'/videos/'+s)
        assert p.exists()

def test_organizefolder(tmpdir):
    options = dict(STDOPTIONSWKEY)
    fixdirectory(options, tmpdir)
    options.update({'destination':str(tmpdir.dirpath())+'/videos_out/'})
    testobj = organizer.Organizer(options)

    createdirstructure(tmpdir)

    testobj.organizefolder(str(tmpdir))

    for s in CORRECTST:
        p = Path(str(tmpdir.dirpath()) + '/videos_out/' + s)
        assert p.exists()