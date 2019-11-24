#! /usr/bin/env python3

# import shutil
from shutil import copy2, move
from os import path, scandir, makedirs, strerror, getcwd
from os import name as osname
from pathlib import Path
import errno
# # import os
# from sys import maxsize
from guessit import guessit
import configparser
import argparse
from re import search, fullmatch
import sys
import logging

import pycountry

# from .cinefiles import Cinefiles

from .tmdb import TMDb, movie, episode
from .export import ExportBash
# from .tmdb import movie

# 
# defaultPath = "/Volumes/Holland Gibson Ext HDD/Movies/Movies"
# path = input("What folder contains the movies you want to rename/place 
# in folders?\n("+defaultPath+"): ")

description = "A utility for organizing a media folder"

class Organizer:

    def __init__(self, args):
        if(len(args)==0):
            raise RuntimeError("No arguments!")

        #find API key
        apisearch = None

        if('apikey' not in args):
            keypath = getcwd() + '/apikey.ini'
            try:
                keyfile = Path(keypath).read_text()
            except FileNotFoundError as e:
                raise FileNotFoundError("No API key file found, try running cinefolders from the command line "+
                                        "("+keypath+")")

            apisearch = search("[0-9a-f]{32}",keyfile)
        else:
            apisearch = search("[0-9a-f]{32}", args['apikey'])

        if(apisearch is None):
            raise OSError("Did not find a valid API key at '" + keypath + "' Try deleting that file and running the "
                    "command line utility 'cinefolders' again to generate it.")

        self.apikey = apisearch.group(0)
    
        self.optionsdict = dict(args)
        
        self.optionsdict.update({
                'def_lang':'en',
                'def_region':'us',
        })
        
        ########################
        # Initialize Variables #
        ########################

        #create logger
        self.logger = logging.getLogger('cinefolders')
        
        debugLevel = logging.WARNING
        debugFormat = '%(asctime)s:%(levelname)s:%(message)s'

        if(self.debugmode()):
            debugLevel = logging.DEBUG
            debugFormat = '%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'
            #Assume implied verbose
            self.optionsdict.update({'v':True})
        
        self.logger.setLevel(debugLevel)

        # config the logger with custom formatter and console stream
        ch = logging.StreamHandler()
        ch.setLevel(debugLevel)
        formatter = logging.Formatter(debugFormat, datefmt='%H:%M:%S')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        if(self.debugmode()):
            self.logger.debug(str(self.optionsdict))

        self.actions = []

        self.setSrc(self.optionsdict['directory'])

        if (self.optionsdict['destination'] is not None):
            # make sure its a string
            # todo is a bytes path ok?
            self.optionsdict['destination'] = str(self.optionsdict['destination'])

            if (self.optionsdict['destination'][-1] != '/'):
                self.optionsdict['destination'] += '/'
            self.setDest(self.optionsdict['destination'])
        else:
            # set destination to operating directory
            self.setDest(self.optionsdict['directory'])
    
        if(self.running_on_windows()):
            #TODO: add windows support on v1.0
            #TODO basically just move every path reference to Path
            print(  "This code does not handle windows " \
                    "file paths correctly, so it cannot run yet. " \
                    "I am deeply sorry for this, please wait until " \
                    "version 1.0 is released. You could help this " \
                    "version get released faster by contributing to " \
                    "this project at github.com/hgibs/cinefolders")
            sys.exit(1) 
#         maxsize = pow(2,31)

        # set up export
        self.export = (self.optionsdict['x'] is not None)
        if (self.export):
            #implies listonly
            self.optionsdict['l'] = True
            self.exporter = ExportBash(Path(self.optionsdict['x']))
            self.logger.info("Exporting bash script to: "+str(self.exporter.exportLocation))
        else:
            #this class is useful for other things too
            self.exporter = ExportBash(self.optionsdict['directory'].joinpath("export.sh"))
                
        #######################
        # Set class variables #
        #######################
        
        self.tmdb = TMDb(self.apikey,
                        self.optionsdict['def_lang'],
                        self.optionsdict['def_region'])
        
#         self.interactive = not self.configdict['non-interactive']
        
        self.log = []

    def checkDestExists(self,dirpath):
        try:
            Path(dirpath).mkdir(parents=True)
        except FileExistsError as fee:
            if(fee.errno == 17):
                #ignore if dest already exists
                pass
            else:
                raise fee

    def setDest(self,dirpath):
        p = Path(dirpath)
        self.checkDestExists(p)
        self.setPath(p, 'destination')
    
    def setSrc(self,dirpath):
        p = Path(dirpath)
        self.setPath(p, 'directory')

    def setCopy(self, value):
        #evaluate to a stricter boolean
        self.configdict.update({'copy':(bool)(value)})
            
    def setPath(self, pathobj, key):

        if(pathobj.exists()):
            if(pathobj.is_dir()):
                #convert to absolute path to avoid possible issues
                self.optionsdict.update({key:pathobj.absolute()})
            else:
                raise NotADirectoryError(errno.ENOTDIR, strerror(errno.ENOTDIR), str(pathobj))
        else:
            raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), str(pathobj))
    
#     def readconfigs(self, file):
#         config = configparser.ConfigParser()
#         
#         if path.exists(file):
#             config.read(file)
#         else:
#             print('Config file not found!!')

#         
#         if 'cinefolders' not in config:
#             print(  "You must have a [cinefolders] section in the"
#                     +"config file!!!")

#         
#         conf = config['cinefolders']
#         
#         folder = conf.get('mainfolder',fallback='')
#         self.configdict.update({'dirpath':folder})
#         srcfolder = conf.get('source_folder',fallback='')
#         self.configdict.update({'srcpath':srcfolder})
#         copy_flag = conf.getboolean('copy',fallback=True)
#         self.configdict.update({'copy':copy_flag})


    def organize(self):
        copy = self.optionsdict['copy']
        
        srcfolder = self.optionsdict['directory']
        dstfolder = self.optionsdict['destination']
        if(srcfolder == dstfolder and copy):
            raise RuntimeError("Source and destination folders are the same, cannot " \
            "copy in place. Files can only be moved/renamed in the same folder.")
                
        if not path.exists(srcfolder):
            raise NotADirectoryError(srcfolder+" does not exist (source folder)")
        if not path.exists(dstfolder):
            self.checkDestExists(dstfolder)
        
        num = 0
        
        
#         if(not copy):
#             confirmtxt = ""
#             message =   "This product is still in beta, don't " \
#                         "trust this program to not irrecoverably corrupt " \
#                         "your files while moving/renaming. Copying is safer. "
#             
#             if(not self.configdict['accept-risk']):
#                 if(self.interactive):
#                     while(not (confirmtxt=="yes" or confirmtxt=="no")):
#                         confirmtxt = input(message+"Are you sure you want to proceed " \
#                                         "with moving movies into folders? (yes or no) ")
#                         confirmtxt = confirmtxt.lower()
#                         if(not (confirmtxt=="yes" or confirmtxt=="no")):
#                             print("Please enter 'yes' or 'no'")
#                 else:
#                     raise ValueError(message + " To acknowledge this in non-interactive " \
#                                     "mode, please run with 'accept-risk=True' " \
#                                     "config file/command line argument set.")
#             else:
#                 if(self.interactive):
#                     print("Beta risk accepted! Moving files instead of copying")
                
        num = self.organizefolder(srcfolder)
        print()
                
        if(copy):
            returnstmt = str(num)+" videos copied into better-named folders."
        else:
            returnstmt = str(num)+" videos moved into better-named folders."

        if(self.export) : self.exporter.writeout()

        print(returnstmt)     
    
    def printStatus(self, txt):
        if(self.optionsdict['v']):
              self.logger.info(txt)          

    # def debug(self, *msg):
    #     if(self.debugmode()):
    #         for m in msg:
    #             print(m,end='')
    #             print('\t',end='')
    #         print()

    def logaction(self,orig,final):
        self.actions.append(str(orig)+' > '+str(final))

    def printactions(self):
        for a in self.actions:
            print(a)

    def organizefolder(self,src,num=0):
        # limit = self.configdict['limit']
        list = scandir(src) 
        outlist = []
        copy = self.optionsdict['copy'] 
        
        dirpath = str(self.optionsdict['destination'])
        
        listonly = self.optionsdict['l']

        #TODO add non-video files or unknown files to destination (like bring notes, posters, etc along to destination
        #TODO this means we have to ignore non-video files for a search

        for item in list:
            if(not self.debugmode()):
                print(".",end='',flush=True)
            self.logger.debug('>'*50)
            self.logger.debug(item.path)
            if(not item.name.startswith('.')): #ignore hidden files
                if(item.is_file()):
                    #TODO add tmdb_id file
                    endpath = self.fixnameinfo(item)
                    finalpath = Path(dirpath+'/'+endpath)

                    if(not listonly):
                        if(not finalpath.exists()):
                            self.printStatus('Creating directory '+str(finalpath))
                            makedirs(finalpath)
                    else:
                        outlist.append(finalpath)
                    
                    if(not listonly):
                        if(copy):
                            self.exporter.addCopy(Path(item.path), finalpath)
                            self.printStatus('Copying to '+str(finalpath))
                            copy2(item.path, finalpath)
                        else:
                            self.exporter.addMove(Path(item.path), finalpath)
                            self.printStatus('Moving to '+str(finalpath))
                            move(item.path, finalpath)
                    else:
                        if(copy):
                            self.exporter.addCopy(Path(item.path), finalpath)
                        else:
                            self.exporter.addMove(Path(item.path), finalpath)
                        self.printStatus(item.name+' > '+str(finalpath))
                    num+=1
                    self.logaction(item.name,finalpath)
                else:
                    #directory - recursive search
                    num += self.organizefolder(item.path,num)
        return num
                
            
#     def renameexisting(self):
#         folders = scandir(src)
#         for item in folders:
#             if(item.is_folder()):
#                 if(not item.name.startswith('.')):
#                

    def getHigherDirNames(self, it):
        #TODO stop when at specified folder
        pathstr = str(it.path)
        pathcutoff = pathstr.split(str(self.optionsdict['directory']))[-1]

        dirnames = pathcutoff.split('/')
        revnames = []
        
        if(it.is_file()):
            dirnames.pop()
            
        for i in dirnames:
            if(len(i)>0):
                revnames.append(i)

        return revnames
    #
    # def searchhigherdirs(self, item, n=0):
    #     #Search .. to see if it is a more reasonable name for a movie
    #     #TODO search for TV shows the same way
    #     dirnames = self.getHigherDirNames(item)
    #     if(len(dirnames)>=n+1):
    #         info = guessit(item.name)
    #         return self.searchitem(info,item.name)
    #     else:
    #         return None

    def createTitle(self, i_info):
        #create our own title
        name = i_info['title']
        words = name.split(' ')
        newName = ''
    
        skips = ['a','an','the','and','but','or','for','nor','on','at',
                'to','from','by']
        punctuation = [',','?','!','.',';',':']
        for w in words:
            addpunctuation = ''
            if(w[-1] in punctuation):
                #punctuation messes up proper typecasing of title words
                addpunctuation = w[-1]
                w=w[:-1]
            if(w.lower() not in skips):
                newName += w.title()+' '+addpunctuation
            else:
                newName += w+' '+addpunctuation
    
        #make sure first word is capitalized
        words2 = newName.split(' ')
        words2[0] = words2[0].title()
        # words2[-1] = words2[-1].title()
        newName = ''
        for w in words2:
            newName += w+' '
        
        newName = newName.strip()
    
#         if(newName[0:4].lower() == 'the '):
#             newName = newName[4:]
#             newName += ', The '
# #         newName = newName.title()
#

        if('year' in i_info):
            year = str(i_info['year'])
            newName = newName.strip()+' ('+year+')'

        return newName

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

        if (not self.checkifmovie(type)):
            #tv show
            searchName = spname
            if (country_code is not None):
                # TMDb can't search TV shows by region so we add it to title
                countryname = pycountry.countries.get(alpha_2=country_code).name
                searchName += ' ' + countryname
            searchResults = self.tmdb.searchTV(searchName, year)
        else:
            #movie
            addOption = {}
            if (country_code is not None):
                addOption.update({'region': country_code})
            searchResults = self.tmdb.searchMovies(spname, year, queryOptions=addOption)

        self.logger.debug(str(spname)+'/'+str(i_info)+' >> '+str(searchResults))
        return searchResults

    def checkifmovie(self,type):
        if (type == 'episode'):
            return False
        elif (type == 'movie'):
            return True
        else:
            raise RuntimeError("type must be episode or movie")

    def buildpath(self, resultitem, originalinfo):
        newName = ''
        newPath = ''

        if (self.checkifmovie(originalinfo['type'])):
            # movie
            newName = resultitem.title
            if(resultitem.year != 0):
                newName += ' (' + str(resultitem.year) + ')'
            # newName += '.' + spname.split('.')[-1]
            newPath = 'Movies/' + newName + '/' + newName
        else:
            # tv show
            newPath = 'TV Shows/' + resultitem.title + '/Season ' + str(originalinfo['season']) + '/' + resultitem.title
            newPath += " S{:02}E{:02}".format(originalinfo['season'],originalinfo['episode'])

            #get episode name info
            epdict = {'tv_id':resultitem.id,'episode_number':int(originalinfo['episode']),
                      'season_number':int(originalinfo['season'])}
            ep = episode.Episode(epdict, self.tmdb)
            ep.fetchinfo()
            newPath += ' '+ep.name

        size = None
        edition = None
        other = None

        if('edition' in originalinfo):
            edition = originalinfo['edition']
        if ('screen_size' in originalinfo):
            size = originalinfo['screen_size']
        if ('other' in originalinfo):
            other = originalinfo['other']

        addedSlash = False

        for extra in [size,edition,other]:
            if(extra is not None):
                if(not addedSlash):
                    newPath += ' -'
                    addedSlash = True
                if(isinstance(extra,list)):
                    for e in extra:
                        newPath += ' '+str(e)
                else:
                    newPath += ' ' + str(extra)

        return newPath

    def contextSearch(self, topresult, guessedTitle, direntryitem):
        #todo search title as TV show to check for better result
        goodscore = 0.80 #constitutes a match good enough to ignore other contextual searches
        scorecutoff = 0.25 #the cutoff to when we give up and don't rename the file

        # topresult = results[0]
        matchvalue = 0
        if(topresult is not None):
            matchvalue = topresult.titleMatchPercentage(guessedTitle)

        info = guessit(direntryitem.name)

        if (matchvalue >= goodscore):
            # pretty solid match - lets assume its correct
            # self.logger.debug("Good title match > " + topresult.title +' * ' + guessedTitle)
            return self.buildpath(topresult, info)
        else:
            # self.logger.debug(str(matchvalue) +" not good enough for '" + topresult.title +"' * '" + guessedTitle+"'")
            #we can try a few other tricks
            scores = [matchvalue]
            data = [(topresult, info)]

            #search the directory path for a better name?
            folders = self.getHigherDirNames(direntryitem)
            n0dir = None
            n1dir = None
            if (len(folders)>0):
                n0dir = folders.pop()
            if (len(folders) > 0):
                n1dir = folders.pop()

            self.logger.debug("Trying search for "+str(n0dir)+' & '+str(n1dir))

            #TODO: properly search for '/TVshow/season 1/episode1.avi' by just concatenating

            #does a search result match a directory name better than the filename?
            n0results = None
            n1results = None
            if(n0dir is not None):
                n0results = self.searchitem(info, str(n0dir))
            if (n1dir is not None):
                n1results = self.searchitem(info, str(n1dir))

            dirsearchresults = [(n0results,str(n0dir)),
                                (n1results,str(n1dir))]

            for rtuple in dirsearchresults:
                if(rtuple[0] is not None):
                    results = rtuple[0]
                    dirsearchname = rtuple[1]
                    if(len(results)>0):
                        value = results[0].titleMatchPercentage(dirsearchname)
                        self.logger.debug(str(results[0])+' | '+str(dirsearchname))
                        scores.append(value)
                        data.append((results[0],info))

            #what if all we are missing is the subtitle?
            #that means we should expect a good match in the beginning
            if (topresult is not None):
                #we need a result to search against
                giventitle = info['title'].lower()
                titleloc = topresult.title.lower().find(giventitle)
                colonloc = topresult.title.lower().find(':')
                self.logger.debug("Context search for subtitle in: '"+giventitle+"' in '"+topresult.title.lower()+"'")
                self.logger.debug(str(titleloc)+', '+str(colonloc))
                if(titleloc>=0):
                    if(colonloc > 0):
                        if(titleloc+len(giventitle) <= colonloc):
                            #our title falls before the subtitle
                            #ignore the subtitle and check the match
                            resulttitlewithoutcolon = topresult.title[0:colonloc].lower()
                            nosubtitlescore = topresult.arbitraryMatchPercentage(resulttitlewithoutcolon,giventitle)
                            #now we add in the RESULT's title (because it has the subtitle)
                            scores.append(nosubtitlescore)
                            data.append((topresult,info))
                        else:
                            #title falls after the colon... lets not use this method for context
                            pass
                    else:
                        #no colon, so maybe we are just missing some major words?
                        #there is too much unknown here so lets ignore it
                        pass
                else:
                    #info['title'] not located in top result - bad news
                    pass

            #What about the country info?
            if ('country' in info):
                country_code = info['country'].alpha2
                countryname = pycountry.countries.get(alpha_2=country_code).name
                newtitle = guessedTitle + ' ' + countryname
                countrymatchvalue = topresult.titleMatchPercentage(newtitle)
                scores.append(countrymatchvalue)
                data.append((topresult,info))

            bestscore = max(scores)

            if(bestscore<scorecutoff):
                info.update({'title':self.createTitle(info),
                             'id':0}) #required metadata
                fakemovie = movie.Movie(info, None)
                return self.buildpath(fakemovie,info)
            else:
                i = scores.index(bestscore)
                dtuple = data[i]
                return self.buildpath(dtuple[0],dtuple[1])


    #create new filename from limited filesystem info
    def fixnameinfo(self, en):
        i_info = guessit(en.name)
        # self.debug(en.name, i_info)
#         newName = i_info['title'].lower()
        guessitTitle = i_info['title']
        newName = ''
        newPath = ''

        searchResults = self.searchitem(i_info,i_info['title'])

        self.logger.debug(searchResults)
        #top result is the best guess
        #TODO: allow for interactive selecting better match?
        if(len(searchResults)>0):
            topresult = searchResults[0]
            # self.logger.debug(topresult)
            spath = self.contextSearch(topresult, guessitTitle, en)
            newPath = spath
        else:
            self.logger.info("No result for '"+guessitTitle+"' in search results")
            spath = self.contextSearch(None, guessitTitle, en)
            newPath = spath
            newName = self.createTitle(i_info)

        if(newPath == ''):
            #we are missing some relevant info so we do our best
            newPath = newName+'/'+newName

        #add extension
        newPath += '.' + i_info['container']

        return newPath
        
    def log_os_op(self,src='',dst=''):
        #blank src means something was created
        #blank dst means something was deleted
        self.log.append((src,dst))
        
    def running_on_windows(self):
        if(osname=='nt'):
            #codecov skip start
            ctypes.windll.kernel32.SetFileAttributesW.argtypes = (
                                        ctypes.c_wchar_p, ctypes.c_uint32)
            return True
            #codecov skip end
        return False
    
    def debugmode(self):
        return self.optionsdict['debug']