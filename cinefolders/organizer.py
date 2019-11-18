#! /usr/bin/env python3

# import logging
# import shutil
from shutil import copy2, move
from os import path, scandir, makedirs, strerror
from os import name as osname
import errno
# # import os
# from sys import maxsize
from guessit import guessit
import configparser
import argparse

# from .cinefiles import Cinefiles

# from guessit import guessit

from .tmdb import TMDb

# 
# defaultPath = "/Volumes/Holland Gibson Ext HDD/Movies/Movies"
# path = input("What folder contains the movies you want to rename/place 
# in folders?\n("+defaultPath+"): ")

TMDB_API_KEY = 'beb6b398540ccc4245a5b4739186a0bb'

description = "A utility for organizing a media folder"

class Organizer:

    def __init__(self, **kwargs):
    
        print(kwargs)
    
        if(self.running_on_windows()):
            #TODO: add windows support
            print(  "This code does not handle windows " \
                    "file paths correctly, so it cannot run yet. " \
                    "I am deeply sorry for this, please wait until " \
                    "version 1.0 is released. You could help this " \
                    "version get released faster by contributing to " \
                    "this project at github.com/hgibs/cinefolders")
            sys.exit(2) 
#         maxsize = pow(2,31)
        
        self.configdict = { 'configfile':'',
                            'dstpath':'',
                            'srcpath':'',
                            'copy':True,
#                             'limit':maxsize,
                            'non-interactive':False,
                            'accept-risk':False,
                            'def_lang':'en',
                            'def_region':'us',
                            'dry-run':False
                            }
        
        ############
        # Set args #
        ############
        
        for k in kwargs:
            if k not in self.configdict:
                raise KeyError(k+" isn't a valid config key")
                
        if('configfile' in kwargs):
            self.configdict.update({'configfile':kwargs['configfile']})
            self.readconfigs(kwargs['configfile'])
        if('dstpath' in kwargs):
            self.setDest(kwargs['dstpath'])
        if('srcpath' in kwargs):
            self.setSrc(kwargs['srcpath'])
        if('copy' in kwargs):
            self.setCopy(kwargs['copy'])
        for k in ['def_lang','def_region','non-interactive','accept-risk','dry-run']:
            if(k in kwargs):
                self.configdict.update({k:kwargs[k]})
        
        if(len(kwargs)==0):
            #no args!
            if(__name__ == '__main__'):
                print(  "Usage: cinefolders [args]\n"\
                        "\n"\
                        "Arguments:\n"\
                        "These follow a key=[value]"
                        "\t "                
                )
                exit(0)
            #assume interactive mode
            self.configdict.update({'non-interactive':False})
            print(  "No arguments, assuming interactive mode. At a minimum, call " \
                    "setSrc('path/to/videos') and setDest('path/to/videos') (these " \
                    "can be the same directory if you want to rename/move files in " \
                    "place) then organize()")
            
        else:
            #make sure minimum args are set
            if(len(self.configdict['srcpath']) < 1):
                raise TypeError("Required argument 'srcpath' not set")
            elif(len(self.configdict['dstpath']) < 1):
                print("argument 'dstpath' not set, using 'srcpath'")
                self.setDest(self.configdict['srcpath'])
                
        #######################
        # Set class variables #
        #######################
        
        self.tmdb = TMDb(TMDB_API_KEY,
                        self.configdict['def_lang'],
                        self.configdict['def_region'])
        
        self.interactive = not self.configdict['non-interactive']
        
        self.log = []
    
    def setDest(self,dirpath):
        self.setPath(dirpath, 'dstpath')
    
    def setSrc(self,dirpath):
        self.setPath(dirpath, 'srcpath')
        
    def setCopy(self, value):
        #evaluate to a stricter boolean
        self.configdict.update({'copy':(bool)(value)})
            
    def setPath(self, dirpath, key):
        if(dirpath[-1]!='/'):
            dirpath += '/'
        if(path.isdir(dirpath)):
            if(path.exists(dirpath)):
                self.configdict.update({key:dirpath})
            else:
                raise NotADirectoryError(errno.ENOTDIR, strerror(errno.ENOTDIR), dirpath)
        else:
            raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), dirpath) 
    
    def readconfigs(self, file):
        config = configparser.ConfigParser()
        
        if path.exists(file):
            config.read(file)
        else:
            print('Config file not found!!')
            exit()
        
        if 'cinefolders' not in config:
            print(  "You must have a [cinefolders] section in the"
                    +"config file!!!")
            exit()
        
        conf = config['cinefolders']
        
        folder = conf.get('mainfolder',fallback='')
        self.configdict.update({'dirpath':folder})
        srcfolder = conf.get('source_folder',fallback='')
        self.configdict.update({'srcpath':srcfolder})
        copy_flag = conf.getboolean('copy',fallback=True)
        self.configdict.update({'copy':copy_flag})
#         numlimit = conf.getint('max_number',fallback=maxsize)
#         self.configdict.update({'limit':numlimit})
        
#         print(self.configdict)

    def organize(self):
        copy=self.configdict['copy']
            
        dryrun = self.configdict['dry-run']
        
        srcfolder = self.configdict['srcpath']
        dstfolder = self.configdict['dstpath']
        if(srcfolder==dstfolder):
            #same folder, cannot copy
            if(copy):
                raise RuntimeError("Source and destination folders are the same, cannot " \
                "copy in place. Files can only be moved/renamed in the same folder.")
                return False
                
        


        if not path.exists(srcfolder):
            raise NotADirectoryError(srcfolder+" does not exist (source folder)")
        if not path.exists(dstfolder):
            raise NotADirectoryError(dstfolder+" does not exist (destination folder)")
    
        
        num = 0
        
        
        if(not copy):
            confirmtxt = ""
            message =   "This product is still in beta, don't " \
                        "trust this program to not irrecoverably corrupt " \
                        "your files while moving/renaming. Copying is safer. "
            
            if(not self.configdict['accept-risk']):
                if(self.interactive):
                    while(not (confirmtxt=="yes" or confirmtxt=="no")):
                        confirmtxt = input(message+"Are you sure you want to proceed " \
                                        "with moving movies into folders? (yes or no) ")
                        confirmtxt = confirmtxt.lower()
                        if(not (confirmtxt=="yes" or confirmtxt=="no")):
                            print("Please enter 'yes' or 'no'")
                else:
                    raise ValueError(message + " To acknowledge this in non-interactive " \
                                    "mode, please run with 'accept-risk=True' " \
                                    "config file/command line argument set.")
            else:
                if(self.interactive):
                    print("Beta risk accepted! Moving files instead of copying")
                
        num = self.organizefolder(srcfolder)
                
        if(copy):
            returnstmt = str(num)+" videos copied into better-named folders."
        else:
            returnstmt = str(num)+" videos moved into better-named folders."
        print(returnstmt)     
                
                
    def organizefolder(self,src,num=0):
        # limit = self.configdict['limit']
        list = scandir(src) 
        copy = self.configdict['copy'] 
        dstfolder = self.configdict['dstpath']
    
        for item in list:
            if(not item.name.startswith('.')): #ignore hidden files
                if(item.is_file()):
                    #TODO add tmdb_id file
                    (newName, tmdb_id) = self.fixnameinfo(item)
            
                    #logging.info(newName)
                    if(not os.path.exists(dirpath+'/'+newName)):
                        print('Creating directory '+dirpath+'/'+newName)
                        makedirs(dirpath+'/'+newName)
                    
                    if(not dryrun):
                        if(copy):
                            print('Copying to '+newName)
                            copy2(item.path, dirpath+'/'+newName+'/'+item.name)
                        else:
                            print('Moving to '+newName)
                            move(item.path, dirpath+'/'+newName+'/'+item.name)
                    else:
                        if(copy):
                            print('(dry run) Copying to '+newName)
                        else:
                            print('(dry run) Moving to '+newName)
                    num+=1
                else:
                    #directory - recursive search
                    num += self.organizefolder(item.path,num)
                
            
#     def renameexisting(self):
#         folders = scandir(src)
#         for item in folders:
#             if(item.is_folder()):
#                 if(not item.name.startswith('.')):
#                

    def getHigherDirNames(self, it):
        dirnames = it.path.split('/')
        revnames = []
        
        if(it.is_file()):
            dirnames.pop()
            
        for i in reversed(dirnames):
            if(len(i)>0)
                revnames.append(i)
        
        return revnames
        
    #create new filename from limited filesystem info
    def fixname(self, en):
        
        i_info = guessit(en.name)
#         newName = i_info['title'].lower()
        name = i_info['title']
        newName = ''
        year = None
        type = i_info['type']
        #TODO: add country search
        if('year' in i_info):
            year = i_info('year')
        tmdb_id = 
            
        searchResults = self.tmdb.search(name,year)
        #top result is the best guess
        #TODO: allow for interactive selecting better match
        topresult = searchResults[0]
        if(topresult.titleMatchPercentage('name')>=0.80)
            #pretty solid match
            newName = topresult.title
            newName += ' ('+str(topresult.year)+')'
            newName += '.'+en.name.split('.')[-1]
        else:
            #create our own title
            words = name.split(' ')
        
            skips = ['a','an','the','and','but','or','for','nor','on','at',
                    'to','from','by']
            punctuation = [',','?','!','.',';',':']
            for w in words:
                addpunctuation = ''
                if(w[-1] in punctuation):
                    addpunctuation = w[-1]
                    w=w[:-1]
                if(w.lower() not in skips):
                    newName += w.title()+' '+addpunctuation
        
            #make sure first and last word is capitalized
            words2 = newName.split(' ')
            words2[0] = words2[0].title()
            words2[-1] = words2[-1].title()
            newName = ''
            for w in words2:
                newName += w+' '
            
            newName = newName.strip()
        
            if(newName[0:4].lower() == 'the '):
                newName = newName[4:]
                newName += ', The '
    #         newName = newName.title()
        

            if('year' in i_info):
                year = str(i_info['year'])
                newName = newName.strip()+' ('+year+')'
        
        return (newName, tmdb_id)
        
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