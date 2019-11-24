cinefolders
===========
[![Build Status](https://travis-ci.org/hgibs/cinefolders.svg?branch=master)](https://travis-ci.org/hgibs/cinefolders)
[![Codecov](https://img.shields.io/codecov/c/github/hgibs/cinefolders/master.svg)](https://codecov.io/gh/hgibs/cinefolders/)

[![pypi version](https://img.shields.io/pypi/v/cinefolders.svg)](https://pypi.python.org/pypi/cinefolders)
[![# of downloads](https://img.shields.io/pypi/dm/cinefolders.svg)](https://pypi.python.org/pypi/cinefolders)

[Changelog](https://github.com/hgibs/cinefolders/releases)

# Description
**cinefolders** is a command-line utility for organizing organizing media folders into a structure formatted for Plex,
Emby, a flash drive, etc.. You can also automate this to automatically add videos to your media folder, keeping
it organized.

It tries to reversibly rename files as best it can to follow guidelines set by MediaBrowser
 for [movies](https://github.com/MediaBrowser/Wiki/wiki/Movie%20naming) and 
[television](https://github.com/MediaBrowser/Wiki/wiki/TV%20naming). As well as provide a 
link to TheMovieDB for more info. 

If you want to get more info like the trailers, posters, reviews, etc.. Just see the 
sister project to this one: [cinefiles](https://github.com/hgibs/cinefiles).

```
cinefolders.py Videos/
```

Changes this unorganized mess:

    /Videos  
      /Down Periscope.mp4
      /Down Periscope_UHD_.mp4
      /Grand Budapest Hotel (2014).mkv
      /Mulan (1998)/  
        /somecrazyunreleatedname.mp4
      /Avatar - 2x02 -.mkv
      /Movies-I-Like/  
        /Horror Movies/
          /The.Shining.1980.US.DC.1080p.BluRay.H264.AAC-RARBG.mp4

... into this:

    /Videos
      /Movies
        /Down Periscope (1996)
          /Down Periscope (1996).mp4
          /Down Periscope (1996) - Ultra HD.mp4
        /Grand Budapest Hotel (2014)
          /Grand Budapest Hotel (2014).mkv
        /Mulan (1998)
          /Mulan (1998).mp4
        /The Shining (1980)  
          /The Shining (1980) - 1080p Director's Cut.mp4
                
      /TV Shows
        /Avatar the Last Airbender 
          /Season 2
            /Avatar the Last Airbender S02E02 The Cave of Two Lovers.mkv
            
Note: You'll need a TMDb API Key (I can't just let all of you use mine!) Its easy to get
here: [themoviedb.org api](https://www.themoviedb.org/settings/api) Plus once you register 
you can contribute to TMDb! Don't worry, just run `cinefolders` and it'll prompt you for it.


```
usage: cinefolders [-h] [-l] [-v] [-x X] [--dry-run] [--copy]
                   [--destination DESTINATION] [--version] [--debug]
                   directory
```

# Options
```
positional arguments:
  directory             Location of folder holding the videos

optional arguments:
  -h, --help            show this help message and exit
  -l                    List new file structure
  -v                    Verbosely list actions
  -x X                  Export all changes as a bash script
  --dry-run             Don't change anything
  --copy                copy instead of just moving files
  --destination DESTINATION
                        specify an alternate destination
  --version             show program's version number and exit
  --debug               debug option (only for developers)
```

