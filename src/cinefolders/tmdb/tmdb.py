from urllib import parse
import requests
import json
import pycountry
import logging
from math import floor
from time import sleep, time

from . import movie, exceptions, season #is this necessary?

class TMDb:
    def __init__(self, api_key, language='en', region='US'):
        self.api_key = api_key
        langs = []
        for lang in pycountry.languages:
            if hasattr(lang, 'alpha_2'):
                langs.append(lang.alpha_2)
                
        self.lang = language[0:2].lower() #ISO 639-1 standard, i.e. 'en'
        if(not self.lang in langs):
            raise Exception(self.lang+" is not a valid ISO-639-1 language code")
            
        self.region = region
        if(region is not None):
            regions = []
            checkregion = region[0:2].upper()
            for country in pycountry.countries:
                if hasattr(country, 'alpha_2'):
                    regions.append(country.alpha_2)
            if(not checkregion in regions):
                raise Exception(region+" is not a valid ISO-3166-1 country code")
            self.region = checkregion
          
        self.safetime = 0.0
        self.process_api_configs()

        self.logger = logging.getLogger('cinefolders')
            
        
    
    def process_api_configs(self):
        query = parse.urlencode({'api_key':self.api_key})
        baseurl = 'https://api.themoviedb.org/3/configuration?'
        fullurl = baseurl+query
        req = self.safeapi(fullurl)
        data = json.loads(req.text)
        
        self.imgbase = data['images']['secure_base_url']
        self.imgsize = 'original'
        self.available_poster_sizes = data['images']['poster_sizes']
        self.available_backdrop_sizes = data['images']['backdrop_sizes']

    def searchMovies(self, title, year=None, queryOptions=None):
        return self.search(title, year=year, queryOptions=queryOptions, type='movie')

    def searchTV(self, title, year=None, queryOptions=None):
        return self.search(title, year=year, queryOptions=queryOptions, type='tv')

    def search(self, title, year=None, queryOptions=None, type='movie'):
        results = []
        #not searching by region, to get maximum results
        api_dict = {'api_key':self.api_key,
                    'query':title}
                    
        if(queryOptions is not None):
            api_dict.update(queryOptions)

        if(year is not None):
            api_dict.update({'year':str(year)})
        query = parse.urlencode(api_dict)
        baseurl = 'https://api.themoviedb.org/3/search/'+type+'?'
        fullurl = baseurl+query
        self.logger.debug(fullurl)
        req = self.safeapi(fullurl)
        data = json.loads(req.text)
        for res in data['results']:
            
            newitem = None
            if(type=='movie'):
                newitem = movie.Movie(res,self)
            elif(type=='tv'):
                newitem = season.Season(res, self)
            else:
                raise KeyError(str(type)+" is not a valid key type for TMDb.search()")
            results.append(newitem)
            
        return results
        
    def getmovie(self, id):
        idnum = int(id)
        return movie.Movie({'id':idnum},self)
        
    def safeapi(self, url, callnum=0):
        thisrequest = requests.get(url)
        if(not thisrequest.ok):
            tdata = json.loads(thisrequest.text)
            if('status_code' in tdata):
                if(tdata['status_code']==7):
                    raise exceptions.APIKeyException(tdata['status_message'])
            raise requests.exceptions.ConnectionError('Request got code '+str(thisrequest.status_code))
            return None
        
        return thisrequest
