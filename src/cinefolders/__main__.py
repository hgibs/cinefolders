#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entry point module
"""

import cinefolders

from .organizer import Organizer

version = cinefolders.__version__

import argparse
import sys
from os import getcwd
from pathlib import Path

import re

class HelpErrParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_usage()
        sys.exit(2)

def organize_directory(options):
    if(options['debug']):
        run = Organizer(options)
        run.organize()
        run.printactions()
    else:
        try:
            run = Organizer(options)
            run.organize()
            run.printactions()
        except Exception as e:
            print(e)
            sys.exit(1)
        
def checkapikey():
    ascii_art = "         _                   __           _       _                     \n        (_)           "+\
                "      / _|         | |     | |                    \n   ___   _   _ __     ___  | |_    ___   | |"+\
                "   __| |   ___   _ __   ___ \n  / __| | | | '_ \\   / _ \\ |  _|  / _ \\  | |  / _` |  / _ \\ | "+\
                "'__| / __|\n | (__  | | | | | | |  __/ | |   | (_) | | | | (_| | |  __/ | |    \\__ \\\n  \\___|"+\
                " |_| |_| |_|  \\___| |_|    \___/  |_|  \\__,_|  \\___| |_|    |___/\n\n"+\
                "                                                       by holland gibson\n\n"



    keypath = getcwd()
#     print(keypath)
    keyfile = Path(keypath+'/apikey.ini')
    if(not keyfile.is_file()):
        print(ascii_art)

        print("Welcome to the cinefolders utility! It searched TMDb to help determine the title and other info "+
              "for the videos you parse. This requires an API key that you must register for yourself. Please visit "+
              "pypi.org/project/cinefolders to get more info.\n")
        #create API file
        f = open(keyfile,"w+")
        key = ''
        validKey = False
        while(not validKey):
            print('Enter your V3 TMDb API Key from https://www.themoviedb.org/settings/api :',end='',flush=True)
            key = input()
            key = key.strip().lower()
            try:
                validKey = (key == re.fullmatch("[0-9a-f]{32}",key).string)
            except AttributeError as e:
                pass
            print(key, validKey)
            if(not validKey):
                print("Wrong key, it should be the V3 key that looks like this: aeb6b697b40c19d835a5b5e09186ae4b \n")

        f.write("TMDB_API_KEY = '"+key+"'\n")
    
def main():
    parser = HelpErrParser( description='Intelligently organize a directory of '
            'movies and/or tv shows to make it easier to read for yourself, or programs '
            'like Plex or Jellyfin.',
                            prog='cinefolders')
#     parser = argparse.ArgumentParser(description='Intelligently organize a directory of '
#             'movies and/or tv shows to make it easier to read for yourself, or programs '
#             'like Plex or Jellyfin.')
    parser.add_argument('-l', action="store_true", help="list new file structure")
    parser.add_argument('-v', action="store_true", help="verbosely list actions")
    parser.add_argument('-x', help="export all changes as a bash script")
    parser.add_argument('--dry-run', action="store_true", help="don't change anything")
    parser.add_argument('--copy', action="store_true", 
            help="copy instead of just moving files")
    parser.add_argument("directory", help="location of folder holding the videos")
    parser.add_argument('--destination', dest='destination', 
            help='specify an alternate destination instead of moving/copying in place')
    parser.add_argument('--version', action='version', version='%(prog)s '+str(version))
    
    parser.add_argument('--debug', action="store_true", help="debug option (for developers)")
    args = parser.parse_args()
    
    checkapikey()
    
    organize_directory(vars(args))
    
if __name__ == '__main__':
    main()