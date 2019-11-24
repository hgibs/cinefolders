import json
from urllib import parse
import requests
import logging

# import movie

# import .
from .item import Item
from .episode import Episode

class Season(Item):
    def __init__(self, initdict, tmdb):
        super().__init__(initdict,tmdb)

        keys = ['backdrop_path', 'created_by', 'episode_run_time', 'first_air_date', 'genres', 'homepage', 'id',
                'in_production', 'languages', 'last_air_date', 'last_episode_to_air', 'name', 'next_episode_to_air',
                'networks', 'number_of_episodes', 'number_of_seasons', 'origin_country', 'original_language',
                'original_name', 'overview', 'popularity', 'poster_path', 'production_companies', 'seasons', 'status',
                'type', 'vote_average', 'vote_count', 'videos', 'images', 'credits', 'alternative_titles']
                
        for k in keys:
            # These are the default keys:
            # backdrop_path
            # first_air_date
            # id
            # name
            # origin_country
            # original_language
            # original_name
            # overview
            # popularity
            # poster_path
            # vote_average
            # vote_count
            # videos
            # images
            if (k not in self.attributes):
                # These are the non-default keys:
                # created_by
                # episode_run_time
                # genres
                # homepage
                # in_production
                # languages
                # last_air_date
                # last_episode_to_air
                # next_episode_to_air
                # networks
                # number_of_episodes
                # number_of_seasons
                # production_companies
                # seasons
                # status
                # type
                # credits
                # alternative_titles
                self.attributes.update({k:''})

        self.name = self.attributes['name']
        self.title = self.name #to make objective programming easier

        self.ftitle = self.name

        if(len(self.attributes['first_air_date'])>=4):
            self.year = int(self.attributes['first_air_date'][0:4])
        else:
            #no release date found :(
            self.year = 0

    def __str__(self):
        return self.ftitle

    def __repr__(self):
        return str(self)

    def fetchinfo(self,complexurl=None):
        if(complexurl is None):
            super().fetchinfo('https://api.themoviedb.org/3/tv/')
        else:
            super().fetchinfo('',complexurl)
        
    def img_base_path(self):
        retstr = self.tmdb.imgbase+self.tmdb.imgsize
        if(retstr is None or retstr == ''):
            return ''
        return retstr
        
    def processjson(self,resultsdict):
        self.attributes.update(resultsdict)

        print(self.attributes)
        exit()
    
        self.runtime = self.attributes['episode_run_time']['0']
        self.status = self.attributes['status']
        self.overview = self.attributes['overview']
        self.title = self.attributes['title']
        self.tagline = self.attributes['tagline']
        self.belongs_to_collection = self.attributes['belongs_to_collection']
        self.backdrops = self.attributes['images']['backdrops']
        if(len(self.backdrops)>0):
            self.backdrop_path = self.img_base_path()+self.attributes['backdrop_path']
        else:
            self.backdrop_path = ''
        self.posters = self.attributes['images']['posters']
        self.original_title = self.attributes['original_title']
        self.original_language = self.attributes['original_language']
        self.poster_path = self.img_base_path()+self.attributes['poster_path']
        self.production_countries = self.attributes['production_countries']
        self.revenue = self.attributes['revenue']
        self.homepage = self.attributes['homepage']
        self.video = self.attributes['video']
        self.imdb_id = self.attributes['imdb_id']
        self.release_date = self.attributes['release_date']
        self.budget = self.attributes['budget']
        self.popularity = self.attributes['popularity']
        self.genres = self.attributes['genres']
        self.production_companies = self.attributes['production_companies']
        self.videos = self.attributes['videos']['results']
        self.adult = self.attributes['adult']
        self.spoken_languages = self.attributes['spoken_languages']
        self.vote_average = self.attributes['vote_average']
        self.id = str(self.attributes['id'])
        
        if(len(self.release_date)>=4):
            self.ftitle = ( self.title+" ("
                            +self.release_date[0:4]+")")
            self.year = int(self.release_date[0:4])
        
        self.alternative_titles = self.attributes['alternative_titles']['titles']
        
        self.trailers = []
        self.clips = []
        for v in self.videos:
            if(v['type'] == 'Clip'):
                self.clips.append(v)
            elif(v['type'] == 'Trailer'):
                self.trailers.append(v)
                
        self.writers = []
        self.directors = []
        self.producers = []
        for person in self.attributes['credits']['crew']:
            if person['department'] == 'Writing':
                self.writers.append(person)
            elif person['department'] == 'Directing':
                self.directors.append(person)
            elif person['department'] == 'Production':
                self.producers.append(person)
            elif person['department'] == 'Lighting':
                pass
            elif person['department'] == 'Sound':
                pass
        
        tempcast = []
        for person in self.attributes['credits']['cast']:
            tempcast.append(person)
            
        #API looks like it sorts, but just to be safe - in order of appearence
        self.cast = sorted(tempcast, key=lambda castperson: castperson['order'])
        
    def getStrippedTitle(self):
        return self.ignoreStartsWithThe(self.name)

    def getepisode(self,season,episodenum):
        ep = Episode({'tv_id':self.id,'season_number':int(season),'episode_number':episodenum},self.tmdb)
        ep.fetchinfo()
        return ep