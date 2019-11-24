from .item import Item

import logging

class Episode(Item):
    def __init__(self, initdict, tmdb):
        self.attributes = {}

        self.tmdb = tmdb

        self.ftitle = ''

        self.attributes.update(initdict)
        # self.id = str(self.attributes['id'])

        # if (len(self.attributes['release_date']) >= 4):
        #   self.ftitle = (self.attributes['title'] + " ("
        #                  + self.attributes['release_date'][0:4] + ")")
        #   self.year = int(self.attributes['release_date'][0:4])
        # else:
        #   # no release date found :(
        #   self.ftitle = self.title
        #   self.year = 0

        self.attributes.update({'videos': {'results': ['']}})
        self.attributes.update({'images': {'results': ['']}})

        self.fetched = False

        self.logger = logging.getLogger('cinefolders')

        keys = ['air_date', 'crew', 'episode_number', 'guest_stars', 'name', 'overview', 'id', 'production_code',
                'season_number', 'still_path', 'vote_average', 'vote_count', 'tv_id']


        for k in keys:
            if(k not in self.attributes):
                self.attributes.update({k: ''})

        if(self.attributes['tv_id'] == '' or self.attributes['season_number'] == '' or
                self.attributes['episode_number'] == ''):
            raise RuntimeError('Episode objects require tv show tv_id, season_number, and episode_number')

    def fetchinfo(self):
        super().fetchinfo('',complexurl='https://api.themoviedb.org/3/tv/'+str(self.attributes['tv_id'])+'/season/'+
                str(self.attributes['season_number'])+'/episode/'+str(self.attributes['episode_number']))

    def processjson(self, resultsdict):
        self.attributes.update(resultsdict)

        self.air_date = self.attributes['air_date']
        self.crew = self.attributes['crew']
        self.episode_number = int(self.attributes['episode_number'])
        self.guest_stars = self.attributes['guest_stars']
        self.name = self.attributes['name']
        self.overview = self.attributes['overview']
        self.id = int(self.attributes['id'])
        self.production_code = self.attributes['production_code']
        self.season_number = int(self.attributes['season_number'])
        self.still_path = self.attributes['still_path']
        self.vote_average = float(self.attributes['vote_average'])
        self.vote_count = int(self.attributes['vote_count'])
        self.tv_id = int(self.attributes['tv_id'])

