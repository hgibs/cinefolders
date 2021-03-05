#!/usr/bin/env python3

# import cinefolders
import os
from cinefolders.organizer import Organizer
options = {
    'apikey'      : os.environ['TMDB_API_KEY'],
    'directory'   : '/Users/holland/Documents/code/testvideos/source',
    'destination' : '/Users/holland/Documents/code/testvideos/output',
    'copy'        : False,
    'debug'       : False,
    'dry_run'     : False,
    'l'           : False,
    'v'           : False,
    'x'           : None,
}

organizer_obj = Organizer(options)
organizer_obj.organize()