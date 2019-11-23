import json
from urllib import parse
import requests
import logging


class Item:
  def __init__(self, initdict, tmdb):
    self.attributes = {}

    self.tmdb = tmdb

    self.ftitle = ''

    self.attributes.update(initdict)
    self.id = str(self.attributes['id'])

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

  def __str__(self):
    return self.ftitle

  def __repr__(self):
    return str(self)

  def fetchinfo(self,baseurl):
    if (not self.fetched):
      langkey = self.tmdb.lang
      if (self.tmdb.region is not None):
        langkey += '-' + self.tmdb.region

      # baseurl = 'https://api.themoviedb.org/3/movie/'
      query = parse.urlencode({'api_key': self.tmdb.api_key,
                               'language': langkey,
                               'include_image_language': self.tmdb.lang + ',null',
                               'append_to_response': 'videos,images,credits,alternative_titles', })
      fullurl = baseurl + self.id + '?' + query
      self.debugquery = fullurl
      req = requests.get(fullurl)
      try:
        data = json.loads(req.text)
        self.processjson(data)
        self.fetched = True
      except json.JSONDecodeError as err:
        logging.critical(err)
        # return bogus info
        self.processjson(self.attributes)
        self.fetched = False

  def img_base_path(self):
    retstr = self.tmdb.imgbase + self.tmdb.imgsize
    if (retstr is None or retstr == ''):
      return ''
    return retstr

  def processjson(self, resultsdict):
    self.attributes.update(resultsdict)

    self.runtime = self.attributes['runtime']
    self.status = self.attributes['status']
    self.overview = self.attributes['overview']
    self.title = self.attributes['title']
    self.tagline = self.attributes['tagline']
    self.belongs_to_collection = self.attributes['belongs_to_collection']
    self.backdrops = self.attributes['images']['backdrops']
    if (len(self.backdrops) > 0):
      self.backdrop_path = self.img_base_path() + self.attributes['backdrop_path']
    else:
      self.backdrop_path = ''
    self.posters = self.attributes['images']['posters']
    self.original_title = self.attributes['original_title']
    self.original_language = self.attributes['original_language']
    self.poster_path = self.img_base_path() + self.attributes['poster_path']
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

    if (len(self.release_date) >= 4):
      self.ftitle = (self.title + " ("
                     + self.release_date[0:4] + ")")
      self.year = int(self.release_date[0:4])

    self.alternative_titles = self.attributes['alternative_titles']['titles']

    self.trailers = []
    self.clips = []
    for v in self.videos:
      if (v['type'] == 'Clip'):
        self.clips.append(v)
      elif (v['type'] == 'Trailer'):
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

    # API looks like it sorts, but just to be safe - in order of appearence
    self.cast = sorted(tempcast, key=lambda castperson: castperson['order'])

  def youtubepath(self, key):
    return "https://www.youtube.com/watch?v=" + key

  def firsttrailer(self):
    if (self.fetched):
      for v in self.trailers:
        if (v['name'].lower().find('trailer') >= 0):
          return self.youtubepath(v['key'])
      raise Exception("No suitable trailer found in trailer list")
    else:
      raise Exception("Item has not been fetched yet!")

  # from https://stackoverflow.com/questions/2460177/edit-distance-in-python
  def levenshteinDistance(self, s1, s2):
    if len(s1) > len(s2):
      s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
      distances_ = [i2 + 1]
      for i1, c1 in enumerate(s1):
        if c1 == c2:
          distances_.append(distances[i1])
        else:
          distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
      distances = distances_
    return distances[-1]

  # def levenshteinDistanceNoCase(self, s1, s2):
  #     return self.levenshteinDistance(s1.lower(),s2.lower())

  def getStrippedTitle(self):
    return self.ignoreStartsWithThe(self.title)

  def ignoreStartsWithThe(self, title):
    # starting a title with "The " is such a common misunderstanding between the producer and
    # normal people that we just ignore it
    # returns lower case title in either case
    checkTitle = title.lower()
    checkTitleWords = checkTitle.split(' ')
    if (checkTitleWords[0] == 'the'):
      newTitle = ''
      for i in range(1, len(checkTitleWords)):
        newTitle += checkTitleWords[i] + ' '
      return newTitle
    else:
      return checkTitle

  def titleMatchPercentage(self, val):
    # not actually a percentage as this can be negative (if title is longer than val)
    # ... but close enough
    fixedTitle = self.getStrippedTitle()
    # self.logger.debug('title:' + self.getStrippedTitle() + ' >> ' + fixedTitle)
    fixedVal = self.ignoreStartsWithThe(val)
    # self.logger.debug('val:' + val + ' >> ' + fixedVal)

    matchValue = 1.0 - (self.levenshteinDistance(fixedTitle, fixedVal) / (float)(len(fixedTitle)))

    self.logger.debug('#' * 50)
    self.logger.debug(fixedTitle)
    self.logger.debug(fixedVal)
    self.logger.debug(matchValue)
    self.logger.debug('#' * 50)

    return matchValue

  def yearDistance(self, intval):
    return abs(self.year - intval)

