cinefolders
===========

[Changelog](https://github.com/hgibs/cinefolders/releases)

For organizing media folders into a structure formatted for Plex, Emby, a flash drive, etc..

It tries to reversibly rename files as best it can to follow guidelines set by MediaBrowser for 
[movies](https://github.com/MediaBrowser/Wiki/wiki/Movie%20naming) and 
[television](https://github.com/MediaBrowser/Wiki/wiki/TV%20naming). As well as provide a 
link to TheMovieDB for more info. 

Changes: 

    /Videos  
      /Down Periscope.mp4
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
        /Down Periscope 
          /movie.mp4
        /Grand Budapest Hotel (2014)
          /Grand Budapest Hotel (2014).mkv
          /tt120467.html
        /Mulan (1998)
          /mulan.mp4
        /The Shining (1980)  
          /The Shining (1980).mp4
        /Pirates of the Caribbean The Curse of the Black Pearl/  
          /blackpearl.mpv
                
    /TV Shows
      /Avatar the Last Airbender 
        /Season 2
          /Avatar the Last Airbender - S02E02 - The Cave of Two Lovers.mkv