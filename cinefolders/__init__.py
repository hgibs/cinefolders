name = "cinefolders"

__all__ = ['organizer']
__version__ = '0.0.6'
__url__ = 'https://github.com/hgibs/cinefolders'

from .organizer import Organizer

from os import name as osname

import sys
##only python3, because I need new OS import
if(sys.version_info[0]<=2):
  print("This script is only for python3.x")
  sys.exit(2)

def running_on_windows():
    if(osname=='nt'):
        #codecov skip start
        ctypes.windll.kernel32.SetFileAttributesW.argtypes = (
                                    ctypes.c_wchar_p, ctypes.c_uint32)
        return True
        #codecov skip end
    return False
  

def version():
    return __version__