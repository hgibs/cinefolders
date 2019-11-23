import json
from urllib import parse
import requests
import logging

# import .
# from . import tmdb



from .item import Item

class Movie(Item):
    def __init__(self, initdict, tmdb):
        super().__init__(initdict, tmdb)

        keys = ['production_companies', 'original_title', 'videos',
                'budget', 'runtime', 'backdrop_path', 'homepage', 'id',
                'release_date', 'adult', 'genres', 'tagline', 'video',
                'poster_path', 'title', 'popularity',
                'production_countries', 'spoken_languages', 'imdb_id',
                'images', 'revenue', 'vote_average', 'overview',
                'vote_count', 'status', 'belongs_to_collection',
                'original_language', 'original_title']

        for k in keys:
            # These are returned with any movie query:
            # original_title
            # videos
            # backdrop_path
            # id
            # release_date
            # adult
            # video
            # poster_path
            # title
            # popularity
            # images
            # vote_average
            # overview
            # vote_count
            # original_language
            # original_title

            if(k not in self.attributes):
                #These are the non-default keys:
                # production_companies
                # budget
                # runtime
                # homepage
                # genres
                # tagline
                # production_countries
                # spoken_languages
                # imdb_id
                # revenue
                # status
                # belongs_to_collection
                self.attributes.update({k:''})

        self.title = self.attributes['title']
            
        # self.attributes.update(initdict)
        # self.id = str(self.attributes['id'])
        # self.title = self.attributes['title']

        if(len(self.attributes['release_date'])>=4):
            self.ftitle = ( self.attributes['title']+" ("
                            +self.attributes['release_date'][0:4]+")")
            self.year = int(self.attributes['release_date'][0:4])
        else:
            #no release date found :(
            self.ftitle = self.title
            self.year = 0

    def __str__(self):
        return self.ftitle

    def __repr__(self):
        return str(self)

    def fetchinfo(self):
        return super().fetchinfo('https://api.themoviedb.org/3/movie/')

    def processjson(self,resultsdict):
        self.attributes.update(resultsdict)
    
        self.runtime = self.attributes['runtime']
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
