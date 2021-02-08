#! /usr/bin/env python3

from .tmdb import TMDb, movie, episode
import organizer

from pathlib import PurePath
from guessit import guessit

import logging

class Searcher:
    MOVIE_TYPE = 0
    TV_TYPE = 1


    """
    Performs all the searches to find the optimal/true name of an object.

    After instantiation, setItem, then use the get* methods to get the found information.
    """

    def __init__(self, org_obj):
        # self.apikey = org_obj.apikey

        # create logger
        self.logger = logging.getLogger('cinefolders')

        debugLevel = logging.WARNING
        debugFormat = '%(asctime)s:%(levelname)s:searcher:%(message)s'

        if(org_obj.debugmode()):
            debugLevel = logging.DEBUG
            debugFormat = '%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'
            #Assume implied verbose
            org_obj.optionsdict.update({'v':True})

        self.tmdb = org_obj.tmdb

        self.item = None
        self.itemtype = None

    def unsetItem(self):
        self.item = None
        self.itemtype = None

    def setItem(self, item):
        """
        Select the Path item to operate on
        :param item: Path object of video file
        :return: None
        """
        self.item = item
        self.logger.info("Operating on item:"+str(item))
        self.guessInfo()

    def getItemType(self):
        return self.itemtype

    def getShortName(self):
        """
        Gets the shortened, correct name for the current item object
        :return: string
        """
        raise NotImplementedError()

    def getFileName(self):
        """
        Returns the full filename in mediabrowser format.
        :return: string
        """
        raise NotImplementedError()

    def getFullPath(self):
        """
        Returns the final filepath to the video.
        :return: PurePath object
        """
        raise NotImplementedError()

    def getDirPath(self):
        """
        Returns a PurePath object to the directory holding the video
        :return: PurePath
        """
        raise NotImplementedError()

    # def scoreName(self, name, tmdb_obj):
    #     """
    #     Rates the given name on how good of a match it is, highest score is most likely to be correct.
    #     :param name: string - name to score
    #     :param tmdb_obj: Tmdb - object to score against
    #     :return: float (range: 0.0-inf)
    #     """


    def guessInfo(self):
        """
        Utilizes all the path information to perform searches and identify the optimal/true name
        :return: None
        """
        guessit_info = guessit(self.item.name)

        self.itemtype = self.MOVIE_TYPE
        self.itemtype = self.TV_TYPE

        raise NotImplementedError()

    def getHigherDirNames(self, it):
        # TODO stop when at specified folder?
        pathstr = str(it.path)
        pathcutoff = pathstr.split(str(self.optionsdict['directory']))[-1]

        dirnames = pathcutoff.split('/')
        revnames = []

        if (it.is_file()):
            dirnames.pop()

        for i in dirnames:
            if (len(i) > 0):
                revnames.append(i)

        return revnames

    def createSelfMadeTitle(self, i_info):
        """
        Creates a self made title using an info dict - without searching the web or anything
        :param i_info: dict
        :return: string
        """

        # create our own title
        name = i_info['title']
        words = name.split(' ')
        newName = ''

        skips = ['a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at',
                 'to', 'from', 'by']
        punctuation = [',', '?', '!', '.', ';', ':']
        for w in words:
            addpunctuation = ''
            if (w[-1] in punctuation):
                # punctuation messes up proper typecasing of title words
                addpunctuation = w[-1]
                w = w[:-1]
            if (w.lower() not in skips):
                newName += w.title() + ' ' + addpunctuation
            else:
                newName += w + ' ' + addpunctuation

        # make sure first word is capitalized
        words2 = newName.split(' ')
        words2[0] = words2[0].title()
        # words2[-1] = words2[-1].title()
        newName = ''
        for w in words2:
            newName += w + ' '

        newName = newName.strip()

        #         if(newName[0:4].lower() == 'the '):
        #             newName = newName[4:]
        #             newName += ', The '
        # #         newName = newName.title()
        #

        if ('year' in i_info):
            year = str(i_info['year'])
            newName = newName.strip() + ' (' + year + ')'

        return newName

    def contextSearch(self, topresult, guessedTitle, direntryitem):
        # todo search title as TV show to check for better result
        goodscore = 0.80  # constitutes a match good enough to ignore other contextual searches
        scorecutoff = 0.25  # the cutoff to when we give up and don't rename the file

        # topresult = results[0]
        matchvalue = 0
        if (topresult is not None):
            matchvalue = topresult.titleMatchPercentage(guessedTitle)

        info = guessit(direntryitem.name)

        if (matchvalue >= goodscore):
            # pretty solid match - lets assume its correct
            # self.logger.debug("Good title match > " + topresult.title +' * ' + guessedTitle)
            return self.buildpath(topresult, info)
        else:
            # self.logger.debug(str(matchvalue) +" not good enough for '" + topresult.title +"' * '" + guessedTitle+"'")
            # we can try a few other tricks
            scores = [matchvalue]
            data = [(topresult, info)]

            # search the directory path for a better name?
            folders = self.getHigherDirNames(direntryitem)
            n0dir = None
            n1dir = None
            if (len(folders) > 0):
                n0dir = folders.pop()
            if (len(folders) > 0):
                n1dir = folders.pop()

            self.logger.debug("Trying search for " + str(n0dir) + ' & ' + str(n1dir))

            # TODO: properly search for '/TVshow/season 1/episode1.avi' by just concatenating

            # does a search result match a directory name better than the filename?
            n0results = None
            n1results = None
            if (n0dir is not None):
                n0results = self.searchitem(info, str(n0dir))
            if (n1dir is not None):
                n1results = self.searchitem(info, str(n1dir))

            dirsearchresults = [(n0results, str(n0dir)),
                                (n1results, str(n1dir))]

            for rtuple in dirsearchresults:
                if (rtuple[0] is not None):
                    results = rtuple[0]
                    dirsearchname = rtuple[1]
                    if (len(results) > 0):
                        value = results[0].titleMatchPercentage(dirsearchname)
                        self.logger.debug(str(results[0]) + ' | ' + str(dirsearchname))
                        scores.append(value)
                        data.append((results[0], info))

            # what if all we are missing is the subtitle?
            # that means we should expect a good match in the beginning
            if (topresult is not None):
                # we need a result to search against
                giventitle = info['title'].lower()
                titleloc = topresult.title.lower().find(giventitle)
                colonloc = topresult.title.lower().find(':')
                self.logger.debug(
                    "Context search for subtitle in: '" + giventitle + "' in '" + topresult.title.lower() + "'")
                self.logger.debug(str(titleloc) + ', ' + str(colonloc))
                if (titleloc >= 0):
                    if (colonloc > 0):
                        if (titleloc + len(giventitle) <= colonloc):
                            # our title falls before the subtitle
                            # ignore the subtitle and check the match
                            resulttitlewithoutcolon = topresult.title[0:colonloc].lower()
                            nosubtitlescore = topresult.arbitraryMatchPercentage(resulttitlewithoutcolon,
                                                                                 giventitle)
                            # now we add in the RESULT's title (because it has the subtitle)
                            scores.append(nosubtitlescore)
                            data.append((topresult, info))
                        else:
                            # title falls after the colon... lets not use this method for context
                            pass
                    else:
                        # no colon, so maybe we are just missing some major words?
                        # there is too much unknown here so lets ignore it
                        pass
                else:
                    # info['title'] not located in top result - bad news
                    pass

                # What about the country info?
                if ('country' in info):
                    country_code = info['country'].alpha2
                    countryname = pycountry.countries.get(alpha_2=country_code).name
                    newtitle = guessedTitle + ' ' + countryname
                    countrymatchvalue = topresult.titleMatchPercentage(newtitle)
                    scores.append(countrymatchvalue)
                    data.append((topresult, info))

            bestscore = max(scores)

            if (bestscore < scorecutoff):
                info.update({'title': self.createTitle(info),
                             'id': 0})  # required metadata
                fakemovie = movie.Movie(info, None)
                return self.buildpath(fakemovie, info)
            else:
                i = scores.index(bestscore)
                dtuple = data[i]
                return self.buildpath(dtuple[0], dtuple[1])

    # create new filename from limited filesystem info by using guessit
    def fixnameinfo(self, en):
        i_info = guessit(en.name)
        pathstr = en.path
        # self.debug(en.name, i_info)
        #         newName = i_info['title'].lower()
        guessitTitle = i_info['title']

        searchResultSet = []

        # search for just title first
        searchResults = self.searchitem(i_info, i_info['title'])
        searchResultSet.append(searchResults)

        # if subtitle found, do multiple searches
        if 'alternative_title' in i_info.keys():
            galt_titles = i_info['alternative_title']
            if isinstance(galt_titles, str):
                subtitle = galt_titles
            elif isinstance(galt_titles, list):
                # search for each subtitle individually
                for alt_title in galt_titles:
                    searchTitle = i_info['title'] + ' ' + alt_title
                    searchResults = self.searchitem(i_info, searchTitle)
                    searchResultSet.append(searchResults)

                # search for a combo
                joinedtitle = i_info['title'] + ' ' + ' '.join(galt_titles)
                searchResults = self.searchitem(i_info, joinedtitle)
                searchResultSet.append(searchResults)
            else:
                self.logger.warn("Could not process alternative title:" + str(galt_titles) + str(i_info))

        newName = ''
        newPath = ''

        self.logger.debug(searchResultSet)
        # top result is the best guess
        # compare all best guesses
        # TODO: allow for interactively selecting better match?
        topresults = []
        for sr in searchResultSet:
            if (len(sr) > 0):
                topresults.append(sr[0])

        if len(topresults) == 0:
            self.logger.info(
                "No result for '" + guessitTitle + "' (and subtitles, if applicable) in search results")
            newPath, newName = self.contextSearch(None, guessitTitle, en)
            # newName = self.createTitle(i_info)
        else:
            # choose best one
            if len(topresults) == 1:
                newPath, newName = self.contextSearch(topresults[0], guessitTitle, en)
            else:
                bestoftr = None
                for tr in topresults:
                    # score the results
                    # todo this is a bad scoring mechanic
                    score_tr = tr.titleMatchPercentage(guessitTitle)
                    if bestoftr is None:
                        bestoftr = (tr, score_tr)
                    else:
                        besttr, best_score = bestoftr
                        if score_tr > best_score:
                            bestoftr = (tr, score_tr)

                selectedSearch, selectedScore = bestoftr
                newPath, newName = self.contextSearch(selectedSearch, guessitTitle, en)

        if (newPath == ''):
            # we are missing some relevant info so we do our best
            newPath = newName + '/'

        # add extension
        newName += '.' + i_info['container']

        return (newPath, newName)

    def searchTvShow(self, year, country_code, spname):
        searchName = spname
        if (country_code is not None):
            # TMDb can't search TV shows by region so we add it to title
            countryname = pycountry.countries.get(alpha_2=country_code).name
            searchName += ' ' + countryname
        return self.tmdb.searchTV(searchName, year)

    def searchMovie(self, year, country_code, spname):
        addOption = {}
        if (country_code is not None):
            addOption.update({'region': country_code})
        self.tmdb.searchMovies(spname, year, queryOptions=addOption)

    def searchitem(self, i_info, spname):
        if(len(spname)==0):
            raise ValueError('name '+str(spname)+' cannot be empty')

        searchResults = None

        year = None
        type = i_info['type']

        if ('year' in i_info):
            year = i_info['year']

        country_code = None
        if ('country' in i_info):
            country_code = i_info['country'].alpha2

        if (self.checkifmovie(type)):
            # movie
            searchResults = self.searchMovie(year, country_code, spname)
        else:
            # tv show
            searchResults = self.searchTvShow(year, country_code, spname)

        if searchResults is None or len(searchResults) == 0:
            #ok lets try searching the opposite video type to get a result
            if (self.checkifmovie(type)):
                # tried as movie before - try tv show now
                searchResults = self.searchTvShow(year, country_code, spname)
            else:
                #tried as tv show before - try movie now
                searchResults = self.searchMovie(year, country_code, spname)

        self.logger.debug(str(spname)+'/'+str(i_info)+' >> '+str(searchResults))
        return searchResults

    def checkifmovie(self,type):
        if (type == 'episode'):
            return False
        elif (type == 'movie'):
            return True
        else:
            raise RuntimeError("type must be episode or movie")