from pathlib import PurePath
import re

imdb_re = re.compile('tt[0-9]+')
num_re = re.compile('[0-9]{3,}')

class VideoID:
    # these numbers also identify the relative importance, i.e. TMDB takes precedence over others
    TMDB_TV=1
    TMDB_MOVIE=2
    IMDB=3
    #TVDB=3
    #TODO: Add TheTVDB by API

    def __init__(self, id, type):
        self.id = id
        if type < 1 or type > 3:
            raise ValueError('illegal type selected, try Id.TMDB_TV, Id.IMDB, or Id.TMDB_MOVIE')
        self.type = type

def createIDFromFile(pathobj):
    #TODO: limit the amount of text read to limit memory problems
    if not isinstance(pathobj, PurePath):
        raise ValueError("rootPath must be a PurePath object")
    rawText = pathobj.read_text()
    type = -1
    id = None
    if rawText.find('imdb') >= 0:
        type = VideoID.IMDB
        id = imdb_re.match(rawText).group()
    elif rawText.find('themoviedb.org') >= 0 or rawText.find('tmdb') >= 0:
        if rawText.find('movie') > 0:
            id = num_re.match(rawText).group()
            type = VideoID.TMDB_MOVIE
        elif rawText.find('tv') > 0:
            #TODO: if episode and season better use API to figure it out!
            id = num_re.match(rawText).group()
            type = VideoID.TMDB_TV
        else:
            raise ValueError("Bad TMDB link, got:\n"+rawText)
    else:
        raise Exception("Couldn't figure out imdb/tmdb id from file given! Please see the readme. Got:\n"+rawText)