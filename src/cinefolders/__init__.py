#!/usr/bin/env python3

name = "cinefolders"

__all__ = ['organizer']
__version__ = '0.1.0'
__url__ = 'https://github.com/hgibs/cinefolders'

import sys

##only python3, because I need new OS import
if(sys.version_info[0]<=2):
    print("This script is only for python3.x")
    sys.exit(2)
  

def version():
    return __version__
    
