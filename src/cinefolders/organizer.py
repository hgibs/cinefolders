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

from .searcher import Searcher

from .tmdb import TMDb, movie, episode
from .export import ExportBash

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

            apisearch = search("[0-9a-f]{32}", keyfile)
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
        debugFormat = '%(asctime)s:%(levelname)s:organizer:%(message)s'

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

        self.searcher = Searcher(self)

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
                    self.searcher.setItem(item)
                    dirpath = self.searcher.getDirPath()
                    endname = self.searcher.getFileName()
                    fullpath = self.searcher.getFullPath()

                    # outputdir = Path(dirpath+'/'+endpath+'/')
                    # outputfilenamepath = outputdir.joinpath(endname)

                    #make sure output directory exists
                    if(not listonly):
                        if(not dirpath.exists()):
                            self.printStatus('Creating directory '+str(dirpath))
                            makedirs(dirpath)
                    else:
                        outlist.append(dirpath)

                    #move/copy file
                    if(not listonly):
                        if(copy):
                            self.exporter.addCopy(Path(item.path), fullpath)
                            self.printStatus('Copying to '+str(fullpath))
                            copy2(item.path, fullpath)
                        else:
                            self.exporter.addMove(Path(item.path), fullpath)
                            self.printStatus('Moving to '+str(fullpath))
                            move(item.path, fullpath)
                    else:
                        if(copy):
                            self.exporter.addCopy(Path(item.path), fullpath)
                        else:
                            self.exporter.addMove(Path(item.path), fullpath)
                        self.printStatus(item.name+' > '+str(fullpath))
                    num += 1
                    self.logaction(item.name, fullpath)
                else:
                    #directory - recursive search
                    if(item.path != dirpath):
                        num += self.organizefolder(item.path)
                    else:
                        print("Skipping the processing of "+str(dirpath)+" because that is the destination.")
        return num


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


    def buildpath(self, resultitem, originalinfo):
        newName = ''
        newPath = ''

        if self.searcher.getItemType() == Searcher.MOVIE_TYPE:
            # movie
            newName = resultitem.title
            if(resultitem.year != 0):
                newName += ' (' + str(resultitem.year) + ')'
            # newName += '.' + spname.split('.')[-1]
            newPath = 'Movies/' + newName
        else:
            # tv show
            newPath = 'TV Shows/' + resultitem.title + '/Season ' + str(originalinfo['season'])
            newName = resultitem.title + " S{:02}E{:02}".format(originalinfo['season'],originalinfo['episode'])

            #get episode name info
            epdict = {'tv_id':resultitem.id,'episode_number':int(originalinfo['episode']),
                      'season_number':int(originalinfo['season'])}
            ep = episode.Episode(epdict, self.tmdb)
            ep.fetchinfo()
            newName += ' '+ep.name

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
                    newName += ' -'
                    addedSlash = True
                if(isinstance(extra,list)):
                    for e in extra:
                        newName += ' '+str(e)
                else:
                    newName += ' ' + str(extra)

        return (newPath, newName)
        
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